# ProjectNekoMuseMeta

Neko Muse Character Meta Distillation - A collection of Python scripts and markdown documentation for generating specialized LLM distillation data from character metadata.

## Overview

This project provides a comprehensive pipeline for processing character metadata and generating training data suitable for LLM (Large Language Model) distillation. It's designed to help create consistent, character-specific datasets for fine-tuning language models.

## Features

- **Character Metadata Extraction**: Extract and structure character information from source files
- **Dataset Preparation**: Generate instruction-response pairs and conversation datasets
- **Multiple Format Support**: Export data in Alpaca, ShareGPT, and JSONL formats
- **Configuration Management**: Flexible configuration system for pipeline customization
- **Comprehensive Documentation**: Detailed guides and examples

## Project Structure

```
ProjectNekoMuseMeta/
├── scripts/              # Python scripts for data processing
│   ├── extract_metadata.py      # Extract character metadata
│   ├── prepare_dataset.py       # Prepare training datasets
│   ├── format_distillation.py   # Format data for distillation
│   └── config_manager.py        # Configuration management
├── docs/                 # Documentation
│   ├── USAGE.md          # Usage guide
│   ├── DATA_FORMATS.md   # Data format specifications
│   └── EXAMPLES.md       # Examples and templates
├── templates/            # Template files
│   └── character_template.json  # Character data template
├── data/                 # Input data directory
│   └── sample_neko_muse.json    # Sample character data
├── output/               # Output directory for generated data
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

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

1. **Initialize configuration**:
```bash
python scripts/config_manager.py --init config.json
```

2. **Extract metadata** from sample character:
```bash
python scripts/extract_metadata.py \
  -i data/sample_neko_muse.json \
  -o output/metadata.json
```

3. **Prepare datasets**:
```bash
python scripts/prepare_dataset.py \
  -m output/metadata.json \
  -o output/datasets/
```

4. **Format for distillation** (Alpaca format):
```bash
python scripts/format_distillation.py \
  -i output/datasets/instruction_pairs.json \
  -o output/alpaca_format.json \
  -f alpaca
```

## Documentation

- **[Usage Guide](docs/USAGE.md)**: Comprehensive usage instructions
- **[Data Formats](docs/DATA_FORMATS.md)**: Detailed format specifications
- **[Examples](docs/EXAMPLES.md)**: Examples and templates

## Scripts

### extract_metadata.py
Extracts character metadata from source files and structures it for processing.

### prepare_dataset.py
Generates training datasets including instruction-response pairs and conversations.

### format_distillation.py
Formats datasets for various LLM distillation frameworks (Alpaca, ShareGPT, JSONL).

### config_manager.py
Manages configuration settings for the entire pipeline.

## Supported Output Formats

- **Alpaca**: Standard instruction format with instruction/input/output fields
- **ShareGPT**: Conversation-style format with human/gpt exchanges
- **JSONL**: One JSON object per line for streaming and processing

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available for use in character-based LLM training projects.

## Getting Help

- Check the [Usage Guide](docs/USAGE.md) for detailed instructions
- See [Examples](docs/EXAMPLES.md) for practical usage examples
- Review [Data Formats](docs/DATA_FORMATS.md) for format specifications

## Example Use Case

Creating distillation data for the "Neko Muse" character to fine-tune an LLM that can respond in-character with consistent personality traits, speaking style, and behavior patterns.
