---
name: qwen-code
description: Delegate tasks to Qwen Code CLI as a subagent for file operations, web research, and code analysis. Use when you need rich built-in tools, high cache efficiency (>95%), 1M context window, and structured JSON output. WARNING: --yolo auto-approves ALL actions - use with caution.
license: Complete terms in LICENSE.txt
---

# Qwen Code Delegation

This skill teaches Claude how to delegate appropriate tasks to Qwen Code CLI (Alibaba's command-line AI assistant) for efficient task distribution.

Qwen Code provides rich built-in tools, high cache efficiency, and structured JSON output. It's ideal for tasks requiring file operations, web research, or data extraction with 1M context window for long documents.

## When to Use This Skill

- **File operations**: Read, write, edit, search files with built-in tools
- **Web research**: Search and fetch web content for information gathering
- **Data extraction**: Gather structured information from various sources
- **Code analysis**: Analyze code patterns, imports, and structure
- **Environment verification**: Check system status, dependencies, and tools
- **Long document processing**: Handle files up to 1M tokens in length

## What This Skill Does

1. **Task delegation**: Teaches Claude when to delegate tasks to Qwen Code vs handling them directly
2. **Command construction**: Shows how to build proper qwen commands with appropriate safety flags
3. **Output parsing**: Guides parsing of Qwen's text or JSON output formats
4. **Safety enforcement**: Implements critical safety measures for the dangerous --yolo flag
5. **Tool selection**: Helps choose between text output for reading vs JSON for programmatic use

## How to Use

### Basic Usage (Text Output)

When Claude identifies a task suitable for Qwen Code, it will construct a command like:

```bash
qwen -p "List all Python files in current directory with sizes and line counts" --yolo -o text
```

### Advanced Usage (JSON Output)

For programmatic processing and data extraction:

```bash
# JSON output for parsing
qwen -p "Read config.json and output as structured data" --yolo -o json

# With safety exclusions for file operations
qwen -p "Analyze project structure" --exclude-tools write_file,edit --yolo -o text

# Using approval modes for safer file operations
qwen -p "Edit configuration file" --approval-mode plan -o text
```

## Example

**User**: "Search for recent best practices about Python type hints"

**Claude (using this skill)**: Delegates to Qwen Code with:

```bash
qwen -p "Search the web for recent best practices about Python type hints and async programming, summarize key points in bullet format" --yolo -o text
```

**Output from Qwen**:
```
Here are recent best practices for Python type hints and async programming:

Type Hints:
• Use typing module for complex types (List[str], Dict[str, Any])
• Add return type annotations for all functions
• Use TypeVar for generic functions
• Consider mypy or pyright for type checking

Async Programming:
• Use asyncio.create_task() instead of ensure_future()
• Always await coroutines properly
• Use async context managers (async with)
• Handle cancellation with asyncio.CancelledError
```

**Inspired by**: Real-world usage of Qwen Code CLI for development and research workflows

## Tips

- **Avoid --yolo for file writes**: Use `--approval-mode default` or `--approval-mode plan` for file operations
- **Use -o json for parsing**: JSON output is structured and easier to process programmatically
- **Monitor cache efficiency**: Check `cache_read_input_tokens` in usage stats (typically >95%)
- **Add timeouts**: Use `timeout 30` to prevent hanging on long tasks
- **Exclude dangerous tools**: Use `--exclude-tools write_file,edit` for read-only tasks

## Common Use Cases

1. **Research automation**: Gather and summarize technical information from the web
2. **Codebase analysis**: Analyze imports, dependencies, and code patterns
3. **Documentation generation**: Extract key information from code for documentation
4. **Environment auditing**: Verify system configurations and installed tools
5. **Data extraction**: Convert unstructured information into structured formats
6. **Long document processing**: Handle large code files or documentation (1M context)

## Key Characteristics

### Strengths
- **Rich Built-in Tools**: Native support for `read_file`, `write_file`, `edit`, `web_search`, `grep_search`, etc.
- **High Cache Efficiency**: Typically >95% cache hit rate (`cache_read_input_tokens` in usage stats)
- **Large Context Window**: 1M context length, suitable for processing long documents and code files
- **Structured Output**: JSON format with detailed metadata (token usage, tool list, execution stats)
- **Fast Execution**: Quick response times due to efficient caching and built-in tool integration
- **Web Capabilities**: Built-in web search and content fetching without external dependencies

### Limitations
- **Auto-approval Risk**: `--yolo` flag automatically approves all actions (potentially dangerous)
- **Less Transparent**: JSON output requires parsing, less human-readable than Kimi's ThinkPart
- **No Directory Isolation**: No `-w` flag for working directory restriction
- **Node.js Dependency**: Requires Node.js/npm installation environment

## Basic Commands

### Check Installation
```bash
qwen --version
qwen --help
```

### Execute Task
```bash
# Non-interactive mode with text output (human readable)
qwen -p "Your task description here" --yolo -o text

# JSON output for programmatic processing
qwen -p "Your task description here" --yolo -o json

# Interactive mode (opens chat interface)
qwen "Your prompt here"
```

## Security Considerations ⚠️

### Qwen Code Security Risks
- **Auto-approval Danger**: `--yolo` flag automatically approves ALL actions including file writes, edits, and deletions
- **Built-in File Operations**: Native `write_file`, `edit` tools can modify or delete files without confirmation
- **No Directory Isolation**: Missing `-w` flag makes it harder to restrict file access scope
- **Web Access**: Built-in `web_search` and `web_fetch` can access external content (potential data leakage)

### Critical Safety Measures

#### 1. Avoid --yolo for File Operations
```bash
# DANGEROUS: Auto-approves file modifications
qwen -p "Edit config file" --yolo -o text

# SAFER: Use approval modes for file operations
qwen -p "Edit config file" --approval-mode default -o text
qwen -p "Edit config file" --approval-mode plan -o text
```

#### 2. Exclude Dangerous Tools
```bash
# Prevent write/delete operations
qwen -p "Task" --exclude-tools write_file,edit --yolo -o text

# Read-only mode (approximate)
qwen -p "Analysis task" --exclude-tools write_file,edit,run_shell_command --yolo -o text
```

#### 3. Implement External Safeguards
```bash
# Use timeout to prevent hanging
timeout 30 qwen -p "Task" --yolo -o text

# Run in restricted directory
cd /safe/workspace && qwen -p "Task" --yolo -o text

# Git protection layer
git add -A && git commit -m "Pre-Qwen-backup" && qwen -p "Task" --yolo -o text
```

### Risk-Based Task Categorization

| Risk Level | Task Type | Safety Measures |
|------------|-----------|-----------------|
| **Low** | Read-only analysis, web search | `--yolo` acceptable, add timeout |
| **Medium** | File reading, code analysis | Use `--approval-mode default`, exclude write tools |
| **High** | File editing, refactoring | Use `--approval-mode plan`, manual review required |
| **Critical** | System changes, deletions | Avoid delegation, handle directly with Claude Code |

## Troubleshooting

### Qwen Not Found
```bash
# Check installation
which qwen
# Expected: ~/.nvm/versions/node/v*/bin/qwen or similar
# If missing, install via npm:
npm install -g @qwen-ai/code
```

### Command Failures
```bash
# Test basic functionality
qwen -p "Say hello" --yolo -o text

# Enable debug mode for detailed logs
qwen -p "Task" --yolo --debug -o text

# Check debug logs location
ls -la ~/.qwen/debug/
```

### JSON Parsing Issues
```bash
# Install jq for JSON parsing if not available
sudo apt-get install jq

# Test JSON parsing
qwen -p "Test JSON output" --yolo -o json | jq .

# Extract specific field
qwen -p "Task" --yolo -o json | jq -r '.[-1].result'
```

## References

- [Qwen Code GitHub Repository](https://github.com/QwenLM/Qwen-Code)
- [Alibaba Qwen Models Documentation](https://qwenlm.github.io/)
- [Qwen Code CLI Documentation](https://help.aliyun.com/zh/model-studio/developer-reference/qwen-code-cli)
