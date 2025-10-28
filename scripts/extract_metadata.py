#!/usr/bin/env python3
"""
Character Metadata Extractor

This script extracts character metadata from source files and prepares it
for LLM distillation. It processes character information including personality
traits, dialogue patterns, and behavioral characteristics.
"""

import json
import argparse
import os
from pathlib import Path
from typing import Dict, List, Any


class CharacterMetadataExtractor:
    """Extract and process character metadata for LLM training."""
    
    def __init__(self, input_path: str, output_path: str):
        """Initialize the extractor.
        
        Args:
            input_path: Path to input character data
            output_path: Path to save extracted metadata
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        
    def load_character_data(self) -> Dict[str, Any]:
        """Load character data from input file.
        
        Returns:
            Dictionary containing character data
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
            
        with open(self.input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from character data.
        
        Args:
            data: Raw character data
            
        Returns:
            Extracted and structured metadata
        """
        metadata = {
            "character_name": data.get("name", "Unknown"),
            "personality_traits": data.get("personality", []),
            "dialogue_examples": data.get("dialogue_samples", []),
            "background": data.get("background", ""),
            "speaking_style": data.get("speaking_style", {}),
            "relationships": data.get("relationships", {}),
            "metadata": {
                "version": "1.0",
                "extraction_source": str(self.input_path)
            }
        }
        return metadata
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save extracted metadata to output file.
        
        Args:
            metadata: Extracted metadata to save
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved to: {self.output_path}")
    
    def process(self) -> None:
        """Run the full extraction process."""
        print(f"Loading character data from: {self.input_path}")
        data = self.load_character_data()
        
        print("Extracting metadata...")
        metadata = self.extract_metadata(data)
        
        print("Saving metadata...")
        self.save_metadata(metadata)
        
        print("Extraction complete!")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract character metadata for LLM distillation"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input character data file (JSON format)"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output path for extracted metadata"
    )
    
    args = parser.parse_args()
    
    extractor = CharacterMetadataExtractor(args.input, args.output)
    extractor.process()


if __name__ == "__main__":
    main()
