---
name: kimi-code
description: Delegate simple to moderate coding tasks to Kimi Code CLI as a subagent for file operations, code summarization, and analysis. Use when you need transparent execution with ThinkPart/ToolCall visibility, safe --print mode, and working directory isolation.
license: Complete terms in LICENSE.txt
---

# Kimi Code Delegation

This skill teaches Claude how to delegate appropriate tasks to Kimi Code CLI (Moonshot AI's command-line programming assistant) for efficient task distribution.

Kimi Code provides transparent execution with detailed ThinkPart reasoning, ToolCall visibility, and StatusUpdate with token usage statistics. It's ideal for tasks where you want to see exactly what the AI is doing.

## When to Use This Skill

- **File operations**: List files, find specific file types, check file sizes
- **Code reading**: Read and summarize code files, explain functions
- **Basic analysis**: Count lines, check imports, analyze simple code patterns
- **Environment checks**: Verify tool installations, check system status
- **Simple testing**: Run basic tests and report results

## What This Skill Does

1. **Task delegation**: Teaches Claude when to delegate tasks to Kimi Code vs handling them directly
2. **Command construction**: Shows how to build proper kimi commands with --print flag for safety
3. **Output parsing**: Guides parsing of Kimi's ThinkPart/ToolCall/StatusUpdate output format
4. **Safety enforcement**: Ensures safe use with --print mode and working directory isolation
5. **Error handling**: Provides fallback strategies when Kimi Code fails

## How to Use

### Basic Usage

When Claude identifies a task suitable for Kimi Code, it will construct a command like:

```bash
kimi -p "List all Python files in current directory with sizes" --print
```

### Advanced Usage

For more complex tasks, use working directory isolation and session continuation:

```bash
# With specific working directory
kimi -w /path/to/project -p "Analyze project structure" --print

# Continue from previous session
kimi -C -p "Continue analysis from last task" --print

# With timeout for safety
timeout 30 kimi -p "Task description" --print
```

## Example

**User**: "List all Python files in the current directory and show their line counts"

**Claude (using this skill)**: Delegates to Kimi Code with:

```bash
kimi -p "Find all .py files in current directory, show their names, sizes, and line counts" --print
```

**Output from Kimi**:
```
ThinkPart(type='think', text='I need to list Python files...')
ToolCall(type='shell', command='find . -name "*.py" -exec wc -l {} \;')
ToolResult(type='result', result='./main.py: 45\n./utils.py: 120\n./test.py: 67')
TextPart(type='text', text='Found 3 Python files:\n- main.py: 45 lines\n- utils.py: 120 lines\n- test.py: 67 lines\nTotal: 232 lines')
StatusUpdate(type='status', token_usage=TokenUsage(input_other=150, output=37, input_cache_read=320))
```

**Inspired by**: Real-world usage of Kimi Code CLI for development workflow automation

## Tips

- **Always use --print**: This prevents accidental approval of destructive actions
- **Use -w for isolation**: Restrict file operations to specific directories
- **Monitor token usage**: Check StatusUpdate for cache efficiency (input_cache_read)
- **Extract TextPart**: The final answer is in the TextPart section of output
- **Have fallbacks**: If Kimi fails, be prepared to handle the task directly

## Common Use Cases

1. **Project onboarding**: Quickly analyze a new codebase structure
2. **Code review prep**: Gather statistics about files to be reviewed
3. **Documentation**: Generate summaries of code files for documentation
4. **Environment setup**: Verify required tools and dependencies are installed
5. **Test automation**: Run simple tests and summarize results

## Key Characteristics

### Strengths
- **Transparent Execution**: Shows detailed ThinkPart reasoning, ToolCall details, and StatusUpdate with token usage
- **Cache Efficiency**: Built-in caching system with `input_cache_read` statistics showing cost savings
- **Safe by Default**: `--print` mode is non-interactive and doesn't auto-approve destructive actions
- **Context Management**: `-w` flag for working directory isolation, `-C` for session continuation
- **Multi-step Reasoning**: Can plan and execute complex multi-step tasks autonomously

### Limitations
- **Slower Output**: Detailed transparency comes at the cost of parsing complexity
- **Tool Dependency**: Relies on external tool calls via Shell for many operations
- **Less Built-in Tools**: Fewer native tools compared to Qwen Code
- **Python Dependency**: Requires Python/uv installation environment

## Basic Commands

### Check Installation
```bash
kimi --version
kimi info
```

### Execute Task
```bash
# Non-interactive mode (for automation)
kimi -p "Your task description here" --print

# With specific working directory
kimi -w /path/to/directory -p "List files" --print

# Continue previous session
kimi -C -p "Continue from last task" --print
```

## Delegation Workflow

### 1. Task Assessment
- Is task well-defined and suitable for Kimi?
- Does `kimi` command exist? (`which kimi`)
- What working directory is needed?

### 2. Command Construction
```bash
# Basic pattern
kimi -p "Clear task description" --print

# Example: File analysis
kimi -p "List all .py files in current directory with their sizes" --print

# Example: Code reading
kimi -p "Read main.py and summarize what it does" --print
```

### 3. Execute and Parse
```bash
# Execute via Bash tool
result=$(kimi -p "Task description" --print 2>&1)

# Check exit code (0 = success)
echo $?
```

### 4. Extract Results
Look for `TextPart` sections in Kimi's output:
```
TextPart(type='text', text='The answer here...')
```

## Security Considerations

### Kimi Code Safety Features
- **Non-interactive by Default**: `--print` mode prevents accidental approval of destructive actions
- **Transparent Tool Execution**: All `ToolCall` and `ToolResult` details are visible in output
- **No Auto-approval**: Unlike Qwen's `--yolo`, Kimi requires explicit approval for risky operations
- **Working Directory Isolation**: `-w` flag limits file operations to specified directory

### Recommended Safety Configuration
```bash
# Safe execution pattern
timeout 30 kimi -w /workspace -p "Read-only task description" --print

# With session continuation for efficiency
kimi -w /workspace -C -p "Continue analysis" --print

# Avoid dangerous patterns
# DON'T: kimi -p "Delete temporary files" --print
# DO: kimi -p "List temporary files that could be deleted" --print
```

## Troubleshooting

### Kimi Not Found
```bash
# Check installation
which kimi

# Expected: ~/.local/bin/kimi or similar
# If missing, install via uv:
uv tool install kimi-cli
```

### Authentication Issues
```bash
# Run login if needed
kimi login
```

### Command Failures
```bash
# Test basic functionality
kimi -p "Say hello" --print

# Check verbose output
kimi -p "Task" --print --verbose
```

## References

- [Kimi Code Documentation](https://moonshotai.github.io/kimi-cli/)
- [Kimi Code GitHub](https://github.com/moonshotai/kimi-cli)
