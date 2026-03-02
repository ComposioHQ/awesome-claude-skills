---
name: qwen-code
description: Delegate tasks to Qwen Code CLI as a subagent for file operations, web research, and code analysis. Use when you need to delegate tasks requiring rich built-in tools, high cache efficiency (>95%), and structured JSON output. WARNING: --yolo auto-approves ALL actions - use with caution.
license: Complete terms in LICENSE.txt
---

# Qwen Code Delegation

This skill enables delegation of appropriate tasks to Qwen Code CLI (Alibaba's command-line AI assistant) for efficient task distribution.

## When to Use

Delegate to Qwen Code for tasks that are:
- **File and code operations**: Reading, writing, editing, searching files
- **Web research**: Search and fetch web content for information gathering
- **Basic to moderate complexity**: Well-defined tasks with clear outputs
- **Data extraction**: Structured information gathering from various sources
- **Routine checks**: Environment verification, dependency checks, system status

### Suitable Tasks
- List files in directory and subdirectories with details
- Find all Python files and analyze their imports
- Read documentation and extract key points
- Search the web for specific technical information
- Check system environment and installed tools
- Run simple tests and summarize results
- Extract data from files into structured formats
- Search codebase for specific patterns or functions

### Keep with Claude Code
- Complex architectural decisions and system design
- Multi-step system integration and deployment
- Security-critical operations and sensitive data handling
- Tasks requiring deep contextual understanding of the codebase
- Team coordination, task management, and workflow orchestration

## Key Characteristics

### Strengths
- **Rich Built-in Tools**: Native support for read_file, write_file, edit, web_search, grep_search, etc.
- **High Cache Efficiency**: Typically >95% cache hit rate (cache_read_input_tokens in usage stats)
- **Large Context Window**: 1M context length, suitable for processing long documents and code files
- **Structured Output**: JSON format with detailed metadata (token usage, tool list, execution stats)
- **Fast Execution**: Quick response times due to efficient caching and built-in tool integration
- **Web Capabilities**: Built-in web search and content fetching without external dependencies

### Limitations
- **Auto-approval Risk**: --yolo flag automatically approves all actions (potentially dangerous)
- **Less Transparent**: JSON output requires parsing, less human-readable than Kimi's ThinkPart
- **No Directory Isolation**: No -w flag for working directory restriction
- **Node.js Dependency**: Requires Node.js/npm environment

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

## Delegation Workflow

### 1. Task Assessment
- Verify task fits "Suitable Tasks" criteria
- Check that qwen command is available: which qwen
- Determine if task requires text or JSON output format

### 2. Command Construction
```bash
# Basic pattern for human-readable output
qwen -p "Clear task description with necessary context" --yolo -o text

# For programmatic processing and data extraction
qwen -p "Structured task expecting JSON output" --yolo -o json

# Example: File system analysis
qwen -p "List all .py files in current directory with their sizes and line counts" --yolo -o text

# Example: Code analysis with structured output
qwen -p "Read main.py and output function signatures as JSON array" --yolo -o json
```

### 3. Execute and Parse
```bash
# Execute via Bash tool
result=$(qwen -p "Task description" --yolo -o text 2>&1)

# Check exit code (0 = success)
echo $?

# For JSON output, parse with jq
json_result=$(qwen -p "Task" --yolo -o json 2>&1)
parsed=$(echo "$json_result" | jq -r '.[-1].result')
```

## Output Parsing

### Text Output Format
Qwen Code provides clean, formatted text output suitable for direct human consumption.

### JSON Output Structure
```json
[
  {
    "type": "system",
    "subtype": "init",
    "tools": ["list_directory", "read_file", "web_search", ...],
    "model": "coder-model"
  },
  {
    "type": "result",
    "subtype": "success",
    "result": "Final answer text",
    "usage": {
      "input_tokens": 13324,
      "output_tokens": 284,
      "cache_read_input_tokens": 13002,
      "total_tokens": 13608
    }
  }
]
```

### Key Fields to Extract
1. **.result**: Complete answer text
2. **.message.content[0].text**: Assistant's text response
3. **.usage**: Token usage statistics for cost monitoring
4. **.tools**: List of available tools (for debugging)

## Examples

### Example 1: Comprehensive File System Analysis
```bash
qwen -p "Find all Python files in the project directory and subdirectories, show their sizes, line counts, last modification dates, and count total lines of Python code" --yolo -o text
```

### Example 2: Code Documentation Extraction
```bash
qwen -p "Read the file src/utils.py and create a structured JSON output containing: function names, parameters, return types, docstrings, and line numbers" --yolo -o json
```

### Example 3: Web Research Task
```bash
qwen -p "Search for recent best practices about Python type hints and async programming, summarize key points in bullet format" --yolo -o text
```

### Example 4: Environment and Dependency Check
```bash
qwen -p "Check Python version, Node.js version, Docker status, list installed Python packages, and verify if git is configured" --yolo -o text
```

## Security Considerations

### Qwen Code Security Risks
- **Auto-approval Danger**: --yolo flag automatically approves ALL actions including file writes, edits, and deletions
- **Built-in File Operations**: Native write_file, edit tools can modify or delete files without confirmation
- **No Directory Isolation**: Missing -w flag makes it harder to restrict file access scope
- **Web Access**: Built-in web_search and web_fetch can access external content (potential data leakage)

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
| **Low** | Read-only analysis, web search | --yolo acceptable, add timeout |
| **Medium** | File reading, code analysis | Use --approval-mode default, exclude write tools |
| **High** | File editing, refactoring | Use --approval-mode plan, manual review required |
| **Critical** | System changes, deletions | Avoid delegation, handle directly with Claude Code |

### Emergency Response
If Qwen starts executing dangerous operations:
1. **Immediate Interrupt**: Ctrl+C to stop execution
2. **Check Git Status**: git status to see file changes
3. **Restore Files**: git checkout -- . to revert modifications
4. **Review Logs**: Check ~/.qwen/debug/ for execution details
5. **Adjust Safety**: Strengthen tool exclusions or switch to approval modes

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
