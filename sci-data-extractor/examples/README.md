# Examples Directory

This directory contains example files to help you get started with Sci-Data-Extractor.

## Files

### sample.pdf
A sample scientific paper PDF for testing the data extraction functionality. This paper contains enzyme kinetics data that can be extracted using the built-in `enzyme` template.

### custom_prompts.txt
A collection of custom extraction prompts for various use cases:
- Protein structure data extraction
- Drug screening data extraction
- Material properties data extraction
- Clinical trial data extraction
- Gene expression data extraction

## Quick Start

### 1. Test with Sample PDF

```bash
# Extract enzyme kinetics data from sample.pdf
python extractor.py examples/sample.pdf --template enzyme -o examples/output.md

# View the results
cat examples/output.md
```

### 2. Use Custom Prompt

```bash
# Extract protein structure data
python extractor.py examples/sample.pdf \
  -p "$(sed -n '1,15p' examples/custom_prompts.txt)" \
  -o examples/protein_data.md
```

### 3. Batch Process Multiple PDFs

```bash
# Create a test directory with multiple PDFs
mkdir -p test_papers
cp examples/sample.pdf test_papers/

# Batch extract
python batch_extract.py test_papers examples/results --template enzyme
```

### 4. Try Different OCR Methods

```bash
# Using PyMuPDF (free, default)
python extractor.py examples/sample.pdf -o examples/pymupdf_output.md

# Using Mathpix OCR (requires API keys)
export MATHPIX_APP_ID="your-app-id"
export MATHPIX_APP_KEY="your-app-key"
python extractor.py examples/sample.pdf --ocr mathpix -o examples/mathpix_output.md
```

## Expected Output

When using the enzyme template on sample.pdf, you should get a Markdown table with columns:

| Enzyme | Organism | Substrate | Km | Unit_Km | Kcat | Unit_Kcat | Kcat_Km | Unit_Kcat_Km | Temperature | pH | Mutant | Cosubstrate |
|--------|----------|-----------|-----|---------|------|-----------|---------|--------------|-------------|-----|--------|-------------|

## Troubleshooting

### PDF Not Found
Make sure you're running the command from the project root directory:
```bash
cd /path/to/sci-data-extractor
python extractor.py examples/sample.pdf --template enzyme -o output.md
```

### API Key Error
Set your API key in the environment:
```bash
export EXTRACTOR_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Mathpix OCR Not Working
Mathpix OCR requires valid API credentials. If you don't have them, use the default PyMuPDF method instead:
```bash
python extractor.py examples/sample.pdf --template enzyme -o output.md
```

## Advanced Examples

### Extract Specific Table Data

```bash
python extractor.py examples/sample.pdf \
  -p "Extract all data from Table 2, including enzyme names, Km values, and their units" \
  -o examples/table2_data.md
```

### Extract with Custom Temperature

```bash
# Lower temperature = more deterministic output
python extractor.py examples/sample.pdf --template enzyme --temperature 0.0 -o examples/output_deterministic.md

# Higher temperature = more creative output
python extractor.py examples/sample.pdf --template enzyme --temperature 0.3 -o examples/output_creative.md
```

### Extract and Output CSV

```bash
python extractor.py examples/sample.pdf --template enzyme -o examples/output.csv --format csv
```

## Contributing Examples

Have a good example PDF or extraction prompt? Feel free to contribute!

1. Fork the repository
2. Add your example files to the `examples/` directory
3. Update this README with documentation
4. Submit a pull request

## Notes

- The sample.pdf is from the original Automated Enzyme Kinetics Extractor project
- All example PDFs should be small (< 5MB) for quick testing
- Custom prompts should be clear and specific about what data to extract
