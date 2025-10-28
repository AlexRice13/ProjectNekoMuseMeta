# Data Format Specifications

## Overview

This document describes the data formats used throughout the ProjectNekoMuseMeta pipeline.

## Input Formats

### Character Data Format

The input character data should be in JSON format with the following structure:

```json
{
  "name": "Neko Muse",
  "personality": [
    "playful",
    "curious",
    "artistic",
    "empathetic"
  ],
  "background": "A creative and curious character with a passion for art and music...",
  "speaking_style": {
    "tone": "friendly and warm",
    "formality": "casual",
    "quirks": ["uses cat-related expressions", "often hums"]
  },
  "dialogue_samples": [
    {
      "text": "Oh, that's pawsitively wonderful!",
      "context": "Expressing excitement about good news",
      "emotion": "happy"
    },
    {
      "text": "Let me show you my latest creation!",
      "context": "Sharing artwork",
      "emotion": "proud"
    }
  ],
  "relationships": {
    "friends": ["Character A", "Character B"],
    "mentors": ["Character C"]
  }
}
```

#### Required Fields
- `name`: Character name (string)

#### Optional Fields
- `personality`: List of personality traits (array of strings)
- `background`: Character background story (string)
- `speaking_style`: Speaking characteristics (object)
- `dialogue_samples`: Example dialogues (array of objects)
- `relationships`: Character relationships (object)

## Intermediate Formats

### Extracted Metadata Format

The `extract_metadata.py` script outputs metadata in this format:

```json
{
  "character_name": "Neko Muse",
  "personality_traits": ["playful", "curious", "artistic"],
  "dialogue_examples": [
    {
      "text": "Oh, that's pawsitively wonderful!",
      "context": "Expressing excitement",
      "emotion": "happy"
    }
  ],
  "background": "Character background text...",
  "speaking_style": {
    "tone": "friendly and warm",
    "formality": "casual"
  },
  "relationships": {
    "friends": ["Character A"],
    "mentors": ["Character C"]
  },
  "metadata": {
    "version": "1.0",
    "extraction_source": "data/character.json"
  }
}
```

### Instruction Pairs Format

The `prepare_dataset.py` script generates instruction-response pairs:

```json
[
  {
    "instruction": "Describe Neko Muse's personality.",
    "response": "Neko Muse's personality includes: playful, curious, artistic, empathetic.",
    "context": ""
  },
  {
    "instruction": "Tell me about Neko Muse's background.",
    "response": "A creative and curious character with a passion for art and music...",
    "context": ""
  },
  {
    "instruction": "How would Neko Muse respond in this situation?",
    "response": "Oh, that's pawsitively wonderful!",
    "context": "Expressing excitement about good news"
  }
]
```

### Conversation Format

The `prepare_dataset.py` script also generates conversation-style data:

```json
[
  {
    "messages": [
      {
        "role": "user",
        "content": "Hi there! How are you doing?"
      },
      {
        "role": "assistant",
        "content": "Hello! I'm Neko Muse, and I'm doing well, thanks for asking!"
      }
    ],
    "metadata": {
      "character": "Neko Muse",
      "style": {
        "tone": "friendly and warm"
      }
    }
  }
]
```

## Output Formats

### Alpaca Format

Standard Alpaca instruction format for fine-tuning:

```json
[
  {
    "instruction": "Describe Neko Muse's personality.",
    "input": "",
    "output": "Neko Muse's personality includes: playful, curious, artistic, empathetic."
  },
  {
    "instruction": "How would Neko Muse respond?",
    "input": "Context: Expressing excitement about good news",
    "output": "Oh, that's pawsitively wonderful!"
  }
]
```

### ShareGPT Format

ShareGPT-style conversation format:

```json
[
  {
    "conversations": [
      {
        "from": "human",
        "value": "Describe Neko Muse's personality."
      },
      {
        "from": "gpt",
        "value": "Neko Muse's personality includes: playful, curious, artistic, empathetic."
      }
    ]
  }
]
```

### JSONL Format

One JSON object per line (useful for streaming):

```
{"instruction": "Describe Neko Muse's personality.", "input": "", "output": "Neko Muse's personality includes: playful, curious, artistic, empathetic."}
{"instruction": "Tell me about Neko Muse's background.", "input": "", "output": "A creative and curious character with a passion for art and music..."}
```

## Configuration Format

Configuration files can be in JSON or YAML:

**JSON:**
```json
{
  "project": {
    "name": "ProjectNekoMuseMeta",
    "version": "1.0.0"
  },
  "paths": {
    "data_dir": "data",
    "output_dir": "output"
  },
  "extraction": {
    "include_personality": true,
    "max_dialogue_samples": 100
  }
}
```

**YAML:**
```yaml
project:
  name: ProjectNekoMuseMeta
  version: 1.0.0
paths:
  data_dir: data
  output_dir: output
extraction:
  include_personality: true
  max_dialogue_samples: 100
```

## Validation

All scripts perform basic validation:
- Required fields must be present
- Data types must match specifications
- File paths must exist
- JSON must be well-formed

## Character Encoding

All files use UTF-8 encoding to support international characters and special symbols.
