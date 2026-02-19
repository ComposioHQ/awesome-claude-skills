---
name: Mistral AI Automation
description: "Automate Mistral AI operations -- manage files and libraries, upload documents for fine-tuning, batch processing, and OCR, track fine-tuning jobs, and build RAG pipelines via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Mistral AI Automation

Automate your Mistral AI workflows -- upload files for fine-tuning, batch processing, and OCR, manage document libraries for RAG-enabled agents, list and retrieve files, track fine-tuning jobs, and integrate Mistral AI into cross-app data pipelines.

**Toolkit docs:** [composio.dev/toolkits/mistral_ai](https://composio.dev/toolkits/mistral_ai)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Mistral AI account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. Upload Files to Mistral AI

Use `MISTRAL_AI_UPLOAD_FILE` to upload files for fine-tuning, batch processing, or OCR.

```
Tool: MISTRAL_AI_UPLOAD_FILE
Inputs:
  - file: object (required)
    - name: string -- destination filename (e.g., "training_data.jsonl")
    - mimetype: string -- MIME type (e.g., "application/pdf", "application/jsonl")
    - s3key: string -- S3 key of a previously downloaded/stored file
  - purpose: "fine-tune" | "batch" | "ocr" (default "fine-tune")
```

**Limits:** Maximum file size is 512 MB. For fine-tuning, only `.jsonl` files are supported.

### 2. List and Retrieve Files

Use `MISTRAL_AI_LIST_FILES` to browse uploaded files with pagination, and `MISTRAL_AI_RETRIEVE_FILE` to get metadata for a specific file.

```
Tool: MISTRAL_AI_LIST_FILES
Inputs:
  - limit: integer (optional, min 1)
  - after: string (file ID cursor for next page)
  - order: "asc" | "desc" (default "desc")

Tool: MISTRAL_AI_RETRIEVE_FILE
Inputs:
  - file_id: string (required) -- UUID obtained from List Files
```

### 3. Create Document Libraries

Use `MISTRAL_AI_CREATE_LIBRARY` to group documents into libraries for use with RAG-enabled Mistral AI agents.

```
Tool: MISTRAL_AI_CREATE_LIBRARY
Inputs:
  - name: string (required) -- e.g., "Project Documents"
  - description: string (optional)
```

### 4. Upload Documents to a Library

Use `MISTRAL_AI_UPLOAD_LIBRARY_DOCUMENT` to add documents to a library for RAG retrieval by Mistral AI agents.

```
Tool: MISTRAL_AI_UPLOAD_LIBRARY_DOCUMENT
  - Requires library_id and file details
  - Call RUBE_GET_TOOL_SCHEMAS for full input schema before use
```

### 5. List Libraries and Download Files

Use `MISTRAL_AI_LIST_LIBRARIES` to discover available document libraries, and `MISTRAL_AI_DOWNLOAD_FILE` to retrieve file content.

```
Tool: MISTRAL_AI_LIST_LIBRARIES
  - Lists all document libraries with metadata (id, name, document counts)
  - Call RUBE_GET_TOOL_SCHEMAS for full input schema

Tool: MISTRAL_AI_DOWNLOAD_FILE
  - Downloads raw binary content of a previously uploaded file
  - Call RUBE_GET_TOOL_SCHEMAS for full input schema
```

### 6. Track Fine-Tuning Jobs

Use `MISTRAL_AI_GET_FINE_TUNING_JOBS` to list and filter fine-tuning jobs by model, status, and creation time.

```
Tool: MISTRAL_AI_GET_FINE_TUNING_JOBS
  - Supports filtering by model, status, creation time, and W&B integration
  - Call RUBE_GET_TOOL_SCHEMAS for full input schema
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Fine-tune file format | Only `.jsonl` files are supported for fine-tuning uploads. Other formats will be rejected. |
| File size limit | Maximum upload size is 512 MB per file. |
| File object structure | `MISTRAL_AI_UPLOAD_FILE` requires an `s3key` referencing a previously stored file, not raw binary content. Use a download action first to stage files in S3. |
| Pagination cursors | `MISTRAL_AI_LIST_FILES` uses cursor-based pagination via the `after` parameter (file ID). Continue fetching until no more results are returned. |
| Library document processing | Uploaded library documents are processed asynchronously. They may not be immediately available for RAG queries after upload. |
| Schema references | Several tools (`MISTRAL_AI_UPLOAD_LIBRARY_DOCUMENT`, `MISTRAL_AI_LIST_LIBRARIES`, `MISTRAL_AI_GET_FINE_TUNING_JOBS`, `MISTRAL_AI_DOWNLOAD_FILE`) require calling `RUBE_GET_TOOL_SCHEMAS` to load full input schemas before execution. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `MISTRAL_AI_UPLOAD_FILE` | Upload files for fine-tuning, batch processing, or OCR |
| `MISTRAL_AI_LIST_FILES` | List uploaded files with pagination |
| `MISTRAL_AI_RETRIEVE_FILE` | Get metadata for a specific file by ID |
| `MISTRAL_AI_DOWNLOAD_FILE` | Download content of an uploaded file |
| `MISTRAL_AI_CREATE_LIBRARY` | Create a document library for RAG |
| `MISTRAL_AI_LIST_LIBRARIES` | List all document libraries with metadata |
| `MISTRAL_AI_UPLOAD_LIBRARY_DOCUMENT` | Add a document to a library for RAG |
| `MISTRAL_AI_GET_FINE_TUNING_JOBS` | List and filter fine-tuning jobs |

---

*Powered by [Composio](https://composio.dev)*
