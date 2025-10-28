import argparse
import asyncio
import json
import os
import random
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Set


class PromptLoadError(RuntimeError):
    """Raised when a system prompt cannot be loaded from disk."""


import pandas as pd
from openai import AsyncOpenAI
from tqdm import tqdm

from prompt_dropout import prompt_dropout


def load_system_prompt_from_markdown(path: str) -> str:
    """Read a system prompt from a Markdown file."""

    if not path:
        raise PromptLoadError("system prompt path must be provided")
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        raise PromptLoadError(f"system prompt file not found: {path}")
    try:
        with open(expanded_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except OSError as exc:
        raise PromptLoadError(f"failed to read system prompt: {path}") from exc
    if not content:
        raise PromptLoadError(f"system prompt file is empty: {path}")
    return content


def _resolve_system_prompt(
    base_prompt: Optional[str], system_prompt_markdown: Optional[str]
) -> str:
    """Resolve the system prompt, preferring Markdown file contents when provided."""

    if system_prompt_markdown:
        return load_system_prompt_from_markdown(system_prompt_markdown)

    if isinstance(base_prompt, str) and base_prompt.strip():
        expanded_path = os.path.expanduser(base_prompt)
        if os.path.isfile(expanded_path):
            return load_system_prompt_from_markdown(base_prompt)
        return base_prompt

    try:
        return role_prompt  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError(
            "system prompt must be provided via Markdown path, base_prompt, or role_prompt"
        ) from exc


@dataclass
class CacheRecord:
    """Represents an instruction waiting to be processed."""

    instruction: str


def _make_record(q: str, output_text: str) -> Dict[str, str]:
    return {"instruction": q, "input": "", "output": output_text if output_text else "[EMPTY]"}


async def _call_one(
    client: AsyncOpenAI,
    model: str,
    q: str,
    include_cot: bool,
    think_tag: str,
    max_retries: int,
    base_prompt: str,
    dropout_rate: float = 0.5,
) -> Dict[str, str]:
    retries = 0
    while retries < max_retries:
        try:
            if dropout_rate > 0:
                sys_prompt = prompt_dropout(base_prompt, dropout_rate)
            else:
                sys_prompt = base_prompt
            resp = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": q},
                ],
                extra_body={"enable_thinking": True},
                temperature=0.7,
                max_tokens=512,
            )
            raw = resp.model_dump()
            ch = raw["choices"][0]
            msg = ch.get("message", {}) or {}
            answer = (msg.get("content") or "").strip()
            cot = (msg.get("reasoning_content") or ch.get("reasoning_content") or "").strip()
            if include_cot and cot:
                output_text = f"<{think_tag}>{cot}</{think_tag}>\n{answer}" if answer else f"<{think_tag}>{cot}</{think_tag}>"
            else:
                output_text = answer
            return _make_record(q, output_text)
        except Exception:
            retries += 1
            await asyncio.sleep((2 ** retries) + random.random() * 0.3)
            if retries >= max_retries:
                return _make_record(q, "[ERROR]")
    return _make_record(q, "[ERROR]")


def _load_existing_records(path: str) -> Set[str]:
    processed: Set[str] = set()
    if not os.path.exists(path):
        return processed
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                instruction = item.get("instruction")
                if isinstance(instruction, str) and instruction:
                    processed.add(instruction)
    except Exception:
        # Ignore corrupted cache; caller will handle warning/logging.
        return set()
    return processed


def _file_needs_leading_newline(path: str) -> bool:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    try:
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            return last_char not in (b"\n", b"\r")
    except OSError:
        return False


def _flush_results(path: str, buffer: List[Dict[str, str]]) -> None:
    if not buffer:
        return
    add_leading_newline = _file_needs_leading_newline(path)
    with open(path, "a", encoding="utf-8") as f:
        if add_leading_newline:
            f.write("\n")
        for idx, record in enumerate(buffer):
            if idx > 0:
                f.write("\n")
            f.write(json.dumps(record, ensure_ascii=False))
    buffer.clear()


async def generate_sft_async(
    api_base: str,
    api_key: str,
    model: str,
    input_file: str,
    output_file: str,
    batch_size: int = 10,
    sleep_time: float = 0.0,  # 保留兼容参数
    save_every: int = 50,
    resume: bool = True,
    include_cot: bool = True,
    think_tag: str = "think",
    max_retries: int = 3,
    concurrency: int = 10,
    base_prompt: Optional[str] = None,
    system_prompt_markdown: Optional[str] = None,
    dropout_rate: float = 0.5,
) -> None:
    del sleep_time  # 参数兼容：在并发模型中不再逐条 sleep

    if concurrency <= 0:
        raise ValueError("concurrency must be greater than 0")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    if save_every <= 0:
        raise ValueError("save_every must be greater than 0")
    if dropout_rate < 0:
        raise ValueError("dropout_rate must be greater than or equal to 0")

    prompt_source = _resolve_system_prompt(base_prompt, system_prompt_markdown)
    if not prompt_source.strip():
        raise RuntimeError("system prompt must be a non-empty string")

    base_prompt_value = prompt_source

    client = AsyncOpenAI(base_url=api_base, api_key=api_key)

    df = pd.read_excel(input_file)
    questions = df["question"].dropna().tolist()

    processed_set: Set[str] = set()
    existing_count = 0
    if resume and os.path.exists(output_file):
        processed_set = _load_existing_records(output_file)
        existing_count = len(processed_set)
        if existing_count:
            print(f"🔄 发现已有进度，已加载 {existing_count} 条数据")
        else:
            print("⚠️ 现有 JSONL 文件为空或无法读取，重新开始")
    elif not resume and os.path.exists(output_file):
        os.remove(output_file)

    remaining = [q for q in questions if q not in processed_set]

    pbar = tqdm(total=len(questions), desc="生成中", unit="条")
    if existing_count:
        pbar.update(existing_count)

    results_buffer: List[Dict[str, str]] = []
    total_processed = existing_count

    if remaining:
        first_instruction = remaining.pop(0)
        print("🧪 正在测试首条请求，以下为模型输出示例：")
        preview_record = await _call_one(
            client,
            model,
            first_instruction,
            include_cot,
            think_tag,
            max_retries,
            base_prompt_value,
            dropout_rate,
        )
        print("—— 指令 ——")
        print(first_instruction)
        print("—— 模型输出 ——")
        print(preview_record["output"])

        loop = asyncio.get_running_loop()
        user_decision = await loop.run_in_executor(
            None,
            lambda: input("是否继续执行剩余任务？(y/N): ").strip().lower(),
        )
        if user_decision not in {"y", "yes"}:
            print("🚫 用户已取消任务，不会继续批量生成。")
            pbar.close()
            return

        results_buffer.append(preview_record)
        processed_set.add(first_instruction)
        total_processed += 1
        pbar.update(1)

        if len(results_buffer) >= save_every:
            _flush_results(output_file, results_buffer)

    if not remaining and total_processed == len(questions):
        _flush_results(output_file, results_buffer)
        pbar.close()
        print(f"✅ 共生成 {total_processed} 条数据，已保存到 {output_file}")
        return

    question_iter = iter(remaining)
    free_cache: Deque[CacheRecord] = deque()
    inflight: Set[asyncio.Task] = set()

    def fill_cache() -> None:
        while len(free_cache) < batch_size:
            try:
                q = next(question_iter)
            except StopIteration:
                break
            free_cache.append(CacheRecord(instruction=q))

    fill_cache()

    while inflight or free_cache:
        while len(inflight) < concurrency and free_cache:
            record = free_cache.popleft()
            task = asyncio.create_task(
                _call_one(
                    client,
                    model,
                    record.instruction,
                    include_cot,
                    think_tag,
                    max_retries,
                    base_prompt_value,
                    dropout_rate,
                )
            )
            inflight.add(task)

        if not inflight:
            fill_cache()
            if not free_cache:
                break
            continue

        done, pending = await asyncio.wait(inflight, return_when=asyncio.FIRST_COMPLETED)
        inflight = set(pending)
        for task in done:
            rec = task.result()
            results_buffer.append(rec)
            processed_set.add(rec["instruction"])
            total_processed += 1
            pbar.update(1)

        fill_cache()

        if len(results_buffer) >= save_every:
            _flush_results(output_file, results_buffer)
            print(f"💾 已写入缓存：{total_processed}/{len(questions)}")

    # Flush remaining results
    _flush_results(output_file, results_buffer)

    pbar.close()
    print(f"✅ 共生成 {total_processed} 条数据，已保存到 {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="并发调用 OpenAI 兼容 API，批量生成 SFT 数据（JSONL 格式）"
    )
    parser.add_argument("input_file", help="输入 Excel 文件 (含 question 列)")
    parser.add_argument(
        "-o",
        "--output",
        default="sft_data.jsonl",
        help="输出 JSONL 文件 (默认: sft_data.jsonl)",
    )
    parser.add_argument("--api_base", default=os.getenv("API_BASE", ""), help="OpenAI API base URL")
    parser.add_argument("--api_key", default=os.getenv("API_KEY", ""), help="API key")
    parser.add_argument("--model", default=os.getenv("MODEL", ""), help="使用的模型名")
    parser.add_argument("--batch_size", type=int, default=20, help="送入自由缓存的批大小")
    parser.add_argument("--sleep", type=float, default=0.0, help="兼容参数，无实际并发作用")
    parser.add_argument("--save_every", type=int, default=50, help="缓存累计多少条时写回 JSONL")
    parser.add_argument("--no_resume", action="store_true", help="不启用断点续跑")
    parser.add_argument("--no_cot", action="store_true", help="不写入思维链")
    parser.add_argument("--think_tag", default="think", help="思维链标签 (默认 think)")
    parser.add_argument("--concurrency", type=int, default=10, help="并发请求数（建议 2~16 之间按限流调）")
    parser.add_argument("--max_retries", type=int, default=3, help="失败重试次数")
    parser.add_argument(
        "--system_prompt_path",
        "--system_prompt_markdown",
        dest="system_prompt_path",
        default=None,
        help="读取外部 Markdown 文件作为 system prompt",
    )
    parser.add_argument(
        "--dropout_rate",
        type=float,
        default=0.5,
        help="system prompt dropout 概率 (0 表示禁用)",
    )
    args = parser.parse_args()

    asyncio.run(
        generate_sft_async(
            args.api_base,
            args.api_key,
            args.model,
            args.input_file,
            args.output,
            args.batch_size,
            args.sleep,
            args.save_every,
            resume=not args.no_resume,
            include_cot=not args.no_cot,
            think_tag=args.think_tag,
            max_retries=args.max_retries,
            concurrency=args.concurrency,
            system_prompt_markdown=args.system_prompt_path,
            dropout_rate=args.dropout_rate,
        )
    )


if __name__ == "__main__":
    main()
