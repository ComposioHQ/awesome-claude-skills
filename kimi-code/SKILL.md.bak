---
name: kimi-code
description: Delegate tasks to Kimi Code CLI as a subagent for file operations, code summarization, and analysis. Use when you need to delegate simple to moderate coding tasks. Kimi provides transparent execution with ThinkPart/ToolCall visibility, safe --print mode, and working directory isolation.
license: Complete terms in LICENSE.txt
---

# Kimi Code Delegation

This skill enables delegation of appropriate tasks to Kimi Code CLI (Moonshot AI's command-line programming assistant) for efficient task distribution.

## When to Use

Delegate to Kimi Code for tasks that are:
- **Simple to moderate complexity**: File listing, code reading, basic analysis
- **Well-defined**: Clear requirements and expected outputs
- **Independent**: Can be executed without extensive context sharing
- **Resource-efficient**: Benefit from Kimi's caching system

### Suitable Tasks
- List files in directory and subdirectories
- Find all Python files and show their sizes
- Read README.md and summarize key points
- Explain the purpose of a function
- Check if specific tools are installed
- Run simple tests and report results
- Rename variables in a file
- Extract functions from code

### Keep with Claude Code
- Complex architectural decisions
- Multi-step feature implementation
- Security-critical operations
- Tasks requiring deep contextual understanding
- Team coordination and integration

## Key Characteristics

### Strengths
- **Transparent Execution**: Shows detailed ThinkPart reasoning, ToolCall details, and StatusUpdate with token usage
- **Cache Efficiency**: Built-in caching with input_cache_read statistics
- **Safe by Default**: --print mode is non-interactive and doesn't auto-approve destructive actions
- **Context Management**: -w flag for working directory isolation, -C for session continuation
- **Multi-step Reasoning**: Can plan and execute complex multi-step tasks autonomously

### Limitations
- **Slower Output**: Detailed transparency comes at parsing complexity cost
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
- Does kimi command exist? (which kimi)
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
Look for TextPart sections in Kimi's output:
```
TextPart(type='text', text='The answer here...')
```

## Output Parsing

### Key Output Components
1. **TextPart**: Final answer (extract this)
2. **ThinkPart**: Reasoning process (debugging)
3. **ToolCall/ToolResult**: Tool execution details
4. **StatusUpdate**: Token usage statistics

### Token Usage Monitoring
```
TokenUsage(
    input_other=2650,    # Prompt tokens
    output=37,           # Response tokens
    input_cache_read=5376,  # Cache hits (saves cost)
    input_cache_creation=0  # Cache writes
)
```

## Examples

### Example 1: File System Analysis
```bash
kimi -p "Find all .py files in the project, show line counts and last modified dates" --print
```

### Example 2: Code Documentation
```bash
kimi -p "Read src/utils.py and create a table of functions with their parameters and return types" --print
```

### Example 3: Environment Check
```bash
kimi -p "Check Python version, pip availability, and list installed packages" --print
```

### Example 4: Test Summary
```bash
kimi -p "Run pytest on tests/ and summarize which tests passed/failed" --print
```

## Security Considerations

### Kimi Code Safety Features
- **Non-interactive by Default**: --print mode prevents accidental approval of destructive actions
- **Transparent Tool Execution**: All ToolCall and ToolResult details are visible in output
- **No Auto-approval**: Unlike Qwen's --yolo, Kimi requires explicit approval for risky operations
- **Working Directory Isolation**: -w flag limits file operations to specified directory

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

### Emergency Stop
If Kimi starts executing dangerous operations:
1. **Send SIGINT**: Ctrl+C to interrupt the process
2. **Check output**: Review ToolCall sections for executed commands
3. **Verify files**: Check if any files were modified or deleted
4. **Use git**: If working in git repository, git status and git checkout -- . to restore

## Integration Pattern

```bash
# Pseudo-implementation for delegation
delegate_to_kimi() {
    local task="$1"
    local workdir="${2:-.}"
    
    if ! command -v kimi &> /dev/null; then
        echo "Kimi Code not found, handling task directly"
        return 1
    fi
    
    echo "Delegating to Kimi Code: $task"
    output=$(kimi -w "$workdir" -p "$task" --print 2>&1)
    
    if [ $? -eq 0 ]; then
        # Extract TextPart content
        echo "$output" | grep -A1 "TextPart.*text=" | tail -1 | sed "s/.*text='\(.*\)'.*/\1/"
        return 0
    else
        echo "Kimi Code failed, fallback to direct handling"
        return 1
    fi
}
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
