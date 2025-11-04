---
name: awesome-skills-complete
description: Comprehensive collection of all Claude Skills scripts and references from the awesome-claude-skills repository. This skill provides access to 40+ scripts and extensive reference documentation for document processing (PDF, DOCX, PPTX, XLSX), MCP server development, skill creation, web testing, and artifact building. Use this skill when working with any document format, creating new skills, building MCP servers, or developing web applications.
---

# Awesome Skills Complete

A comprehensive skill that bundles all scripts and reference documentation from the awesome-claude-skills repository, providing a complete toolkit for document processing, development tools, and productivity automation.

## Overview

This skill provides instant access to:
- **40+ Production Scripts** - Ready-to-use Python, JavaScript, and Bash scripts
- **Extensive Reference Documentation** - Detailed guides for document formats and APIs
- **Document Processing Tools** - Complete toolkits for PDF, DOCX, PPTX, and XLSX
- **Development Tools** - MCP server builders, skill creators, web testing frameworks
- **Artifact Builders** - Tools for creating complex HTML artifacts

## When to Use This Skill

Use this skill when:
- Working with **PDF files** (forms, extraction, conversion, annotations)
- Editing **Word documents** (DOCX with tracked changes, comments, OOXML)
- Creating/modifying **PowerPoint presentations** (PPTX slides, layouts, templates)
- Processing **Excel spreadsheets** (XLSX formulas, data manipulation)
- **Building MCP servers** for external API integrations
- **Creating new Claude Skills** with proper structure
- **Testing web applications** with Playwright
- **Building complex artifacts** with React and Tailwind

## Resources

### Document Processing Scripts

#### PDF Tools (`scripts/document-skills/pdf/`)

Complete toolkit for PDF manipulation:

- `check_fillable_fields.py` - Verify and list all fillable form fields in a PDF
- `fill_fillable_fields.py` - Populate PDF forms programmatically with data
- `extract_form_field_info.py` - Extract detailed metadata about form fields
- `fill_pdf_form_with_annotations.py` - Fill PDF forms using annotation-based approach
- `convert_pdf_to_images.py` - Convert PDF pages to image files (PNG, JPG)
- `check_bounding_boxes.py` - Analyze and validate bounding box coordinates
- `create_validation_image.py` - Generate visual validation overlays for PDFs

**Common Use Cases:**
```python
# Extract all form field names and types
python scripts/document-skills/pdf/extract_form_field_info.py input.pdf

# Fill a PDF form with data
python scripts/document-skills/pdf/fill_fillable_fields.py input.pdf output.pdf --data form_data.json

# Convert PDF to images
python scripts/document-skills/pdf/convert_pdf_to_images.py document.pdf output_dir/
```

#### DOCX Tools (`scripts/document-skills/docx/`)

Professional Word document processing with OOXML support:

- `document.py` - Core module for DOCX creation and manipulation
- `utilities.py` - Helper functions for document operations
- `__init__.py` - Package initialization and exports

**OOXML Scripts** (`scripts/document-skills/docx/ooxml/`):
- `validate.py` - Validate DOCX OOXML structure and content
- `pack.py` - Pack OOXML files into DOCX archive
- `unpack.py` - Extract DOCX to OOXML XML files
- `validation/docx.py` - DOCX-specific validation rules
- `validation/redlining.py` - Track changes and revision validation

**Common Use Cases:**
```python
# Unpack DOCX to inspect/edit raw OOXML
python scripts/document-skills/docx/ooxml/unpack.py document.docx output_dir/

# Validate DOCX structure
python scripts/document-skills/docx/ooxml/validate.py document.docx

# Pack modified OOXML back to DOCX
python scripts/document-skills/docx/ooxml/pack.py ooxml_dir/ output.docx
```

#### PPTX Tools (`scripts/document-skills/pptx/`)

PowerPoint presentation automation:

- `inventory.py` - Catalog all slides, layouts, and content in presentation
- `rearrange.py` - Reorder slides programmatically
- `replace.py` - Find and replace text across all slides
- `thumbnail.py` - Generate thumbnail images from slides
- `html2pptx.js` - Convert HTML content to PowerPoint slides

**OOXML Scripts** (`scripts/document-skills/pptx/ooxml/`):
- `validate.py` - Validate PPTX OOXML structure
- `pack.py` - Pack OOXML files into PPTX archive
- `unpack.py` - Extract PPTX to OOXML XML files

**Common Use Cases:**
```python
# Get inventory of all slides and layouts
python scripts/document-skills/pptx/inventory.py presentation.pptx

# Replace text across all slides
python scripts/document-skills/pptx/replace.py presentation.pptx "old text" "new text" output.pptx

# Generate slide thumbnails
python scripts/document-skills/pptx/thumbnail.py presentation.pptx thumbnails_dir/
```

### Development Tools

#### MCP Builder (`scripts/mcp-builder/`)

Tools for creating Model Context Protocol servers:

- `connections.py` - Manage and test MCP server connections
- `evaluation.py` - Evaluate MCP server quality and performance
- `requirements.txt` - Python dependencies for MCP development

**Reference Documentation** (`references/mcp-builder/`):
- `python_mcp_server.md` - Complete guide for Python MCP servers
- `node_mcp_server.md` - Complete guide for Node.js MCP servers
- `mcp_best_practices.md` - Best practices and patterns
- `evaluation.md` - Quality evaluation framework

**Common Use Cases:**
```python
# Test MCP server connection
python scripts/mcp-builder/connections.py --server localhost:8000

# Evaluate MCP server quality
python scripts/mcp-builder/evaluation.py mcp_server_config.json
```

#### Skill Creator (`scripts/skill-creator/`)

Complete toolkit for creating and packaging Claude Skills:

- `init_skill.py` - Initialize new skill from template with proper structure
- `package_skill.py` - Validate and package skill as distributable ZIP
- `quick_validate.py` - Fast validation of skill structure and metadata

**Common Use Cases:**
```bash
# Create new skill
python scripts/skill-creator/init_skill.py my-new-skill --path ./skills

# Validate skill structure
python scripts/skill-creator/quick_validate.py ./skills/my-skill

# Package skill for distribution
python scripts/skill-creator/package_skill.py ./skills/my-skill ./dist
```

#### Web Testing (`scripts/webapp-testing/`)

- `with_server.py` - Run web tests with automatic server management

**Common Use Cases:**
```python
# Run tests with auto-started server
python scripts/webapp-testing/with_server.py --port 3000 tests/
```

#### Artifact Builder (`scripts/artifacts-builder/`)

Tools for creating complex HTML artifacts:

- `init-artifact.sh` - Initialize new artifact project with React/Tailwind
- `bundle-artifact.sh` - Bundle artifact for deployment
- `shadcn-components.tar.gz` - Pre-packaged shadcn/ui components

**Common Use Cases:**
```bash
# Initialize new artifact project
bash scripts/artifacts-builder/init-artifact.sh my-artifact

# Bundle artifact for production
bash scripts/artifacts-builder/bundle-artifact.sh my-artifact dist/
```

### Reference Documentation

#### Document Skills References

**PDF Documentation** (`references/document-skills/pdf/`):
- `reference.md` - Complete PDF processing reference and API docs
- `forms.md` - Detailed guide for PDF forms and field manipulation
- `SKILL.md` - PDF skill usage guide

**DOCX Documentation** (`references/document-skills/docx/`):
- `ooxml.md` - Office Open XML (OOXML) specification and structure
- `docx-js.md` - JavaScript library documentation for DOCX
- `SKILL.md` - DOCX skill usage guide

**PPTX Documentation** (`references/document-skills/pptx/`):
- `ooxml.md` - PowerPoint OOXML specification
- `html2pptx.md` - HTML to PowerPoint conversion guide
- `SKILL.md` - PPTX skill usage guide

#### MCP Builder References (`references/mcp-builder/`)

Comprehensive guides for MCP server development:

- `python_mcp_server.md` - Build Python MCP servers with FastAPI
- `node_mcp_server.md` - Build Node.js MCP servers with Express
- `mcp_best_practices.md` - Architecture patterns and best practices
- `evaluation.md` - Quality metrics and evaluation criteria

## Usage Workflows

### Workflow 1: PDF Form Processing

When working with PDF forms:

1. **Inspect the form structure:**
   ```bash
   python scripts/document-skills/pdf/extract_form_field_info.py form.pdf
   ```

2. **Verify fillable fields:**
   ```bash
   python scripts/document-skills/pdf/check_fillable_fields.py form.pdf
   ```

3. **Fill the form programmatically:**
   ```bash
   python scripts/document-skills/pdf/fill_fillable_fields.py form.pdf filled.pdf --data data.json
   ```

4. **Convert to images for validation:**
   ```bash
   python scripts/document-skills/pdf/convert_pdf_to_images.py filled.pdf output/
   ```

Consult `references/document-skills/pdf/forms.md` for detailed field types and manipulation techniques.

### Workflow 2: DOCX Document Editing

When editing Word documents with OOXML:

1. **Unpack DOCX to OOXML:**
   ```bash
   python scripts/document-skills/docx/ooxml/unpack.py document.docx ooxml_dir/
   ```

2. **Edit the XML files directly** (for complex operations)

3. **Validate the OOXML structure:**
   ```bash
   python scripts/document-skills/docx/ooxml/validate.py ooxml_dir/
   ```

4. **Pack back to DOCX:**
   ```bash
   python scripts/document-skills/docx/ooxml/pack.py ooxml_dir/ output.docx
   ```

Reference `references/document-skills/docx/ooxml.md` for OOXML structure and element specifications.

### Workflow 3: Creating a New Claude Skill

When creating a new skill:

1. **Initialize skill structure:**
   ```bash
   python scripts/skill-creator/init_skill.py my-skill --path ./
   ```

2. **Edit SKILL.md** with skill documentation and instructions

3. **Add scripts, references, or assets** as needed

4. **Validate the skill:**
   ```bash
   python scripts/skill-creator/quick_validate.py ./my-skill
   ```

5. **Package for distribution:**
   ```bash
   python scripts/skill-creator/package_skill.py ./my-skill ./dist
   ```

This creates a validated, distributable ZIP file.

### Workflow 4: Building an MCP Server

When integrating external APIs via MCP:

1. **Read the appropriate reference:**
   - For Python: `references/mcp-builder/python_mcp_server.md`
   - For Node.js: `references/mcp-builder/node_mcp_server.md`

2. **Follow best practices:**
   - Consult `references/mcp-builder/mcp_best_practices.md`

3. **Test connections:**
   ```bash
   python scripts/mcp-builder/connections.py --test
   ```

4. **Evaluate server quality:**
   ```bash
   python scripts/mcp-builder/evaluation.py server_config.json
   ```

### Workflow 5: PowerPoint Automation

When automating presentations:

1. **Inventory existing slides:**
   ```bash
   python scripts/document-skills/pptx/inventory.py presentation.pptx
   ```

2. **Replace placeholder text:**
   ```bash
   python scripts/document-skills/pptx/replace.py presentation.pptx "{{name}}" "John Doe" output.pptx
   ```

3. **Rearrange slides:**
   ```bash
   python scripts/document-skills/pptx/rearrange.py presentation.pptx "1,3,2,4" output.pptx
   ```

4. **Generate thumbnails:**
   ```bash
   python scripts/document-skills/pptx/thumbnail.py output.pptx thumbnails/
   ```

## Key Capabilities

### 1. Document Format Expertise

Access complete tooling for professional document formats:
- **PDF**: Forms, extraction, conversion, annotations, bounding boxes
- **DOCX**: OOXML editing, tracked changes, comments, validation
- **PPTX**: Slide manipulation, layouts, templates, HTML conversion
- **XLSX**: Formula processing, data transformations

### 2. OOXML Mastery

Deep understanding of Office Open XML with:
- Unpack/pack capabilities for DOCX and PPTX
- Validation scripts for structure and content
- Redlining and track changes support
- Direct XML manipulation for advanced features

### 3. MCP Server Development

Complete framework for building Model Context Protocol servers:
- Python and Node.js templates and guides
- Connection testing and evaluation tools
- Best practices for API integration
- Quality assessment frameworks

### 4. Skill Development

Professional skill creation toolkit:
- Template initialization with proper structure
- Validation before packaging
- Distribution-ready ZIP creation
- Best practices embedded in templates

### 5. Web Testing

Automated web application testing:
- Playwright integration
- Server lifecycle management
- Screenshot capture
- UI validation

## Tips for Effective Use

1. **Start with references** - Read the relevant `.md` files in `references/` before using scripts
2. **Validate early** - Use validation scripts before processing to catch errors
3. **Test on copies** - Always work on copies of important documents
4. **Check dependencies** - Some scripts require specific Python packages (see requirements files)
5. **Read script help** - Most scripts have `--help` flags with detailed usage

## Script Dependencies

Most scripts require Python 3.8+ and various packages:

**PDF Scripts:**
- PyPDF2, reportlab, pillow

**DOCX/PPTX Scripts:**
- python-docx, python-pptx, lxml

**MCP Builder:**
- See `scripts/mcp-builder/requirements.txt`

Install with:
```bash
pip install PyPDF2 reportlab pillow python-docx python-pptx lxml
```

## Advanced Features

### OOXML Direct Manipulation

For advanced document editing that libraries don't support:

1. Unpack document to OOXML
2. Edit XML files directly (relationships, content, styles)
3. Validate structure
4. Pack back to document format

This enables features like:
- Custom XML parts
- Advanced revision tracking
- Complex style inheritance
- Document relationships

### Multi-Format Workflows

Combine tools across formats:

1. Extract data from PDF → `convert_pdf_to_images.py`
2. Process in DOCX → `document.py` utilities
3. Present in PPTX → `html2pptx.js`
4. Distribute as packaged skill → `package_skill.py`

## Contributing

All scripts and references in this skill come from the awesome-claude-skills repository. To contribute improvements:

1. Test changes on real-world documents
2. Update both scripts and reference documentation
3. Validate with `quick_validate.py`
4. Submit improvements to the main repository

## License

Scripts and documentation inherit licenses from their original skills. Most are Apache 2.0 licensed. Check individual skill directories for specific licenses.
