#!/usr/bin/env python3
"""
Distillation Data Formatter

This script formats prepared datasets into specific formats required by
various LLM distillation frameworks (e.g., Alpaca format, ShareGPT format).
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any


class DistillationFormatter:
    """Format datasets for different LLM distillation frameworks."""
    
    def __init__(self, input_path: str, output_path: str, format_type: str):
        """Initialize the formatter.
        
        Args:
            input_path: Path to input dataset
            output_path: Path to save formatted output
            format_type: Target format type ('alpaca', 'sharegpt', 'jsonl')
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.format_type = format_type.lower()
        
    def load_dataset(self) -> List[Dict[str, Any]]:
        """Load input dataset.
        
        Returns:
            Dataset as list of dictionaries
        """
        with open(self.input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def format_alpaca(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format data in Alpaca style.
        
        Args:
            data: Input dataset
            
        Returns:
            Alpaca-formatted dataset
        """
        alpaca_data = []
        
        for item in data:
            formatted = {
                "instruction": item.get("instruction", ""),
                "input": item.get("context", ""),
                "output": item.get("response", "")
            }
            alpaca_data.append(formatted)
        
        return alpaca_data
    
    def format_sharegpt(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data in ShareGPT style.
        
        Args:
            data: Input dataset
            
        Returns:
            ShareGPT-formatted dataset
        """
        sharegpt_data = []
        
        for item in data:
            if "messages" in item:
                # Already in conversation format
                formatted = {
                    "conversations": item["messages"]
                }
            else:
                # Convert instruction-response to conversation
                formatted = {
                    "conversations": [
                        {"from": "human", "value": item.get("instruction", "")},
                        {"from": "gpt", "value": item.get("response", "")}
                    ]
                }
            sharegpt_data.append(formatted)
        
        return sharegpt_data
    
    def format_jsonl(self, data: List[Dict[str, Any]]) -> List[str]:
        """Format data as JSONL (one JSON object per line).
        
        Args:
            data: Input dataset
            
        Returns:
            List of JSON strings
        """
        return [json.dumps(item, ensure_ascii=False) for item in data]
    
    def save_formatted_data(self, data: Any) -> None:
        """Save formatted data to output file.
        
        Args:
            data: Formatted dataset
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.format_type == 'jsonl':
            # Save as JSONL
            with open(self.output_path, 'w', encoding='utf-8') as f:
                for line in data:
                    f.write(line + '\n')
        else:
            # Save as JSON
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Formatted data saved to: {self.output_path}")
    
    def process(self) -> None:
        """Run the formatting process."""
        print(f"Loading dataset from: {self.input_path}")
        data = self.load_dataset()
        
        print(f"Formatting data as: {self.format_type}")
        
        if self.format_type == 'alpaca':
            formatted_data = self.format_alpaca(data)
        elif self.format_type == 'sharegpt':
            formatted_data = self.format_sharegpt(data)
        elif self.format_type == 'jsonl':
            formatted_data = self.format_jsonl(data)
        else:
            raise ValueError(f"Unknown format type: {self.format_type}")
        
        print("Saving formatted data...")
        self.save_formatted_data(formatted_data)
        
        print(f"Formatting complete! ({len(data)} items processed)")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Format datasets for LLM distillation frameworks"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input dataset file"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output path for formatted data"
    )
    parser.add_argument(
        "--format",
        "-f",
        required=True,
        choices=['alpaca', 'sharegpt', 'jsonl'],
        help="Target format type"
    )
    
    args = parser.parse_args()
    
    formatter = DistillationFormatter(args.input, args.output, args.format)
    formatter.process()


if __name__ == "__main__":
    main()
