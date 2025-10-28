# Usage Guide

## Overview

This guide explains how to use the ProjectNekoMuseMeta scripts to generate LLM distillation data for character metadata.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AlexRice13/ProjectNekoMuseMeta.git
cd ProjectNekoMuseMeta
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize Configuration

Create a default configuration file:

```bash
python scripts/config_manager.py --init config.json
```

This creates a `config.json` file with default settings.

### 2. Prepare Character Data

Create a character data file in the `data/` directory (see `templates/character_template.json` for format).

### 3. Extract Metadata

Extract character metadata from your source data:

```bash
python scripts/extract_metadata.py \
  --input data/your_character.json \
  --output output/metadata.json
```

### 4. Prepare Dataset

Generate training datasets from the extracted metadata:

```bash
python scripts/prepare_dataset.py \
  --metadata output/metadata.json \
  --output output/datasets/
```

This creates:
- `output/datasets/instruction_pairs.json` - Instruction-response pairs
- `output/datasets/conversations.json` - Conversation-style data

### 5. Format for Distillation

Format the datasets for your target LLM framework:

```bash
# For Alpaca format
python scripts/format_distillation.py \
  --input output/datasets/instruction_pairs.json \
  --output output/distillation/alpaca_format.json \
  --format alpaca

# For ShareGPT format
python scripts/format_distillation.py \
  --input output/datasets/conversations.json \
  --output output/distillation/sharegpt_format.json \
  --format sharegpt

# For JSONL format
python scripts/format_distillation.py \
  --input output/datasets/instruction_pairs.json \
  --output output/distillation/data.jsonl \
  --format jsonl
```

## Complete Pipeline Example

```bash
# 1. Initialize configuration
python scripts/config_manager.py --init config.json

# 2. Extract metadata
python scripts/extract_metadata.py \
  -i data/neko_muse.json \
  -o output/neko_metadata.json

# 3. Prepare datasets
python scripts/prepare_dataset.py \
  -m output/neko_metadata.json \
  -o output/datasets/

# 4. Format for distillation
python scripts/format_distillation.py \
  -i output/datasets/instruction_pairs.json \
  -o output/distillation/alpaca_format.json \
  -f alpaca
```

## Script Reference

### extract_metadata.py

Extracts character metadata from source files.

**Options:**
- `--input, -i`: Input character data file (JSON format)
- `--output, -o`: Output path for extracted metadata

**Example:**
```bash
python scripts/extract_metadata.py -i data/character.json -o output/metadata.json
```

### prepare_dataset.py

Prepares training datasets from character metadata.

**Options:**
- `--metadata, -m`: Path to character metadata file
- `--output, -o`: Output directory for prepared datasets

**Example:**
```bash
python scripts/prepare_dataset.py -m output/metadata.json -o output/datasets/
```

### format_distillation.py

Formats datasets for LLM distillation frameworks.

**Options:**
- `--input, -i`: Input dataset file
- `--output, -o`: Output path for formatted data
- `--format, -f`: Target format type (alpaca, sharegpt, jsonl)

**Example:**
```bash
python scripts/format_distillation.py -i data.json -o output.json -f alpaca
```

### config_manager.py

Manages configuration settings for the pipeline.

**Options:**
- `--load, -l`: Load configuration from file
- `--save, -s`: Save configuration to file
- `--format, -f`: Output format (json, yaml)
- `--print, -p`: Print current configuration
- `--init, -i`: Initialize default configuration file

**Example:**
```bash
python scripts/config_manager.py --init config.json
python scripts/config_manager.py --load config.json --print
```

## Tips

- Always validate your input data format before processing
- Use the configuration manager to maintain consistent settings
- Keep backups of your original character data
- Test with small datasets before processing large amounts of data
- Check the output files to ensure formatting matches your requirements
