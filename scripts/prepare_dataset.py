#!/usr/bin/env python3
"""
Dataset Preparation Script

This script prepares datasets for LLM distillation by formatting character
metadata into training-ready formats. It generates instruction-response pairs,
conversation examples, and character-consistent dialogue patterns.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple


class DatasetPreparator:
    """Prepare training datasets from character metadata."""
    
    def __init__(self, metadata_path: str, output_dir: str):
        """Initialize the dataset preparator.
        
        Args:
            metadata_path: Path to character metadata file
            output_dir: Directory to save prepared datasets
        """
        self.metadata_path = Path(metadata_path)
        self.output_dir = Path(output_dir)
        
    def load_metadata(self) -> Dict[str, Any]:
        """Load character metadata.
        
        Returns:
            Character metadata dictionary
        """
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_instruction_pairs(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate instruction-response pairs from metadata.
        
        Args:
            metadata: Character metadata
            
        Returns:
            List of instruction-response dictionaries
        """
        pairs = []
        char_name = metadata.get("character_name", "Character")
        personality = metadata.get("personality_traits", [])
        background = metadata.get("background", "")
        
        # Generate personality description pairs
        if personality:
            pairs.append({
                "instruction": f"Describe {char_name}'s personality.",
                "response": f"{char_name}'s personality includes: {', '.join(personality)}."
            })
        
        # Generate background pairs
        if background:
            pairs.append({
                "instruction": f"Tell me about {char_name}'s background.",
                "response": background
            })
        
        # Generate dialogue-based pairs from examples
        dialogue_samples = metadata.get("dialogue_examples", [])
        for i, sample in enumerate(dialogue_samples[:5]):  # Limit to 5 examples
            pairs.append({
                "instruction": f"How would {char_name} respond in this situation?",
                "response": sample.get("text", ""),
                "context": sample.get("context", "")
            })
        
        return pairs
    
    def generate_conversation_dataset(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate conversation-style training data.
        
        Args:
            metadata: Character metadata
            
        Returns:
            List of conversation examples
        """
        conversations = []
        char_name = metadata.get("character_name", "Character")
        speaking_style = metadata.get("speaking_style", {})
        
        # Create conversation templates
        base_conversations = [
            {
                "messages": [
                    {"role": "user", "content": "Hi there! How are you doing?"},
                    {"role": "assistant", "content": f"Hello! I'm {char_name}, and I'm doing well, thanks for asking!"}
                ],
                "metadata": {"character": char_name, "style": speaking_style}
            }
        ]
        
        conversations.extend(base_conversations)
        return conversations
    
    def save_dataset(self, data: Any, filename: str) -> None:
        """Save dataset to file.
        
        Args:
            data: Dataset to save
            filename: Output filename
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Dataset saved to: {output_path}")
    
    def process(self) -> None:
        """Run the full dataset preparation process."""
        print(f"Loading metadata from: {self.metadata_path}")
        metadata = self.load_metadata()
        
        print("Generating instruction-response pairs...")
        instruction_pairs = self.generate_instruction_pairs(metadata)
        self.save_dataset(instruction_pairs, "instruction_pairs.json")
        
        print("Generating conversation dataset...")
        conversations = self.generate_conversation_dataset(metadata)
        self.save_dataset(conversations, "conversations.json")
        
        print("Dataset preparation complete!")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Prepare datasets for LLM distillation from character metadata"
    )
    parser.add_argument(
        "--metadata",
        "-m",
        required=True,
        help="Path to character metadata file"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output directory for prepared datasets"
    )
    
    args = parser.parse_args()
    
    preparator = DatasetPreparator(args.metadata, args.output)
    preparator.process()


if __name__ == "__main__":
    main()
