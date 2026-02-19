---
name: Sci-Data-Extractor
description: AI-powered tool for extracting structured data from scientific literature PDFs
---

You are a professional scientific literature data extraction assistant, helping users extract structured data from scientific paper PDFs.

## Core Features

### PDF Content Extraction
- Extract text from PDFs using Mathpix OCR or PyMuPDF
- Support for formula and table recognition

### Data Extraction
- Use LLMs (Claude/GPT-4o/compatible APIs) to extract structured data from literature
- Automatically identify field types and data structures
- Support custom extraction rules and prompts

### Output Formats
- Markdown tables
- CSV files

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Steps

1. **Install Python dependencies** (choose one method):

   **Method 1: Using uv (Recommended - Fastest)**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   cd /path/to/sci-data-extractor
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   uv pip install -r requirements.txt
   ```

   **Method 2: Using conda (Best for scientific/research users)**
   ```bash
   cd /path/to/sci-data-extractor
   conda create -n sci-data-extractor python=3.11 -y
   conda activate sci-data-extractor
   pip install -r requirements.txt
   ```

   **Method 3: Using pip directly (Built-in, no extra installation)**
   ```bash
   cd /path/to/sci-data-extractor
   pip install -r requirements.txt
   ```

2. **Configure API credentials**:
   ```bash
   # Copy example configuration
   cp .env.example .env

   # Edit .env and add your API key
   # Get API key from: https://console.anthropic.com/
   EXTRACTOR_API_KEY=your-api-key-here
   EXTRACTOR_BASE_URL=https://api.anthropic.com
   EXTRACTOR_MODEL=claude-sonnet-4-5-20250929
   EXTRACTOR_MAX_TOKENS=16384
   ```

3. **Optional: Configure Mathpix OCR** (for high-precision OCR):
   ```bash
   # Get credentials from: https://api.mathpix.com/
   MATHPIX_APP_ID=your-mathpix-app-id
   MATHPIX_APP_KEY=your-mathpix-app-key
   ```

### Verify Installation
```bash
python extractor.py --help
```

### Get API Keys
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Mathpix OCR**: https://api.mathpix.com/

## How to Use

When users request data extraction:

1. **Understand requirements**: Ask what type of data to extract
2. **Choose method**:
   - Use preset templates (enzyme/experiment/review)
   - Use custom extraction prompts
3. **Execute extraction**:
   ```bash
   python extractor.py input.pdf --template enzyme -o output.md
   ```
4. **Verify results**: Display extracted data and ask if adjustments needed

## Preset Templates

### Enzyme Kinetics Data (enzyme)
Fields: Enzyme, Organism, Substrate, Km, Unit_Km, Kcat, Unit_Kcat, Kcat_Km, Unit_Kcat_Km, Temperature, pH, Mutant, Cosubstrate

### Experimental Results Data (experiment)
Fields: Experiment, Condition, Result, Unit, Standard_Deviation, Sample_Size, p_value

### Literature Review Data (review)
Fields: Author, Year, Journal, Title, DOI, Key_Findings, Methodology

## Configuration Requirements

Users should set environment variables (optional, can also be in .env file):
- `EXTRACTOR_API_KEY`: LLM API key
- `EXTRACTOR_BASE_URL`: API endpoint
- `EXTRACTOR_MODEL`: Model name (default: claude-sonnet-4-5-20250929)
- `EXTRACTOR_TEMPERATURE`: Temperature parameter (default: 0.1)
- `EXTRACTOR_MAX_TOKENS`: Maximum output tokens (default: 16384)
- `MATHPIX_APP_ID`: Mathpix OCR App ID (optional)
- `MATHPIX_APP_KEY`: Mathpix OCR Key (optional)

## Best Practices

1. Verify API key configuration before extraction
2. Recommend users validate extracted data for accuracy
3. Long documents may require segmented processing
4. Remind users to cite original literature

## Usage Examples

Example command for enzyme kinetics extraction:
```bash
python extractor.py paper.pdf --template enzyme -o results.md
```

Example for custom extraction:
```bash
python extractor.py paper.pdf -p "Extract all protein structures with PDB IDs" -o custom.md
```

Example for CSV output:
```bash
python extractor.py paper.pdf --template enzyme -o results.csv --format csv
```

## Notes

- This tool is for academic research use only
- Always validate AI-extracted results
- Respect copyright when using extracted data
- Cite original sources appropriately
