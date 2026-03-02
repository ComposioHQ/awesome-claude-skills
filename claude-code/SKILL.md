---
name: claude-code
description: "Delegate tasks to Claude Code CLI as a subagent for complex coding tasks, code review, architectural decisions, security analysis, and multi-file refactoring. Claude provides deep reasoning, extensive tool support, and high-quality code generation."
---

# Claude Code Delegation Skill

Delegate appropriate tasks to Claude Code CLI for efficient task distribution.

## Overview

Claude Code is Anthropic's command-line AI assistant that provides:
- Deep reasoning and analysis for complex problems
- Multi-file code generation and refactoring
- Comprehensive code review and security analysis
- Architecture design and system planning
- Integration with skills, agents, and MCP servers
- Tool-based execution with safety controls

## Key Characteristics

### Strengths
- **Deep Reasoning**: Excellent for complex architectural decisions and system design
- **Tool Extensibility**: Rich tool system with skills, agents, and MCP support
- **Code Quality**: High-quality code generation following best practices
- **Security Focus**: Built-in security review and best practice enforcement
- **Multi-file Context**: Handles complex multi-file refactoring tasks
- **Session Management**: Persistent sessions with continuation support

### Limitations
- **Slower for Simple Tasks**: Overhead may be excessive for trivial operations
- **Requires Setup**: Needs proper configuration for best results
- **Higher Cost**: More capable but potentially more expensive for simple tasks
- **Permission System**: May require user approval for sensitive operations

### Performance Profile
- **Typical Response Time**: 10-30 seconds for complex tasks
- **Tool Support**: Extensive (Bash, Read, Write, Edit, Grep, Glob, Task, MCP, etc.)
- **Context Window**: Large context handling for complex multi-file operations
- **Output Quality**: High-quality, well-reasoned responses with detailed explanations

## When to Delegate to Claude Code

Use Claude Code for tasks that are:
- **Complex architectural decisions**: System design, API design, database schema
- **Multi-file refactoring**: Changes spanning multiple files with dependencies
- **Code review and security analysis**: Deep analysis of code quality and security
- **Complex debugging**: Issues requiring deep contextual understanding
- **Documentation generation**: Comprehensive docs from code analysis
- **Test generation**: Comprehensive test suites with edge cases

### Suitable Task Examples
- `Review this codebase for security vulnerabilities`
- `Refactor the authentication system to use JWT tokens`
- `Design an API for a new microservice`
- `Analyze this code for performance bottlenecks`
- `Generate comprehensive tests for this module`
- `Document the architecture of this system`

### Keep with Direct Execution
- Simple file operations (use Bash directly)
- Quick grep searches (use Grep tool)
- Single-line edits (use Edit tool)
- Very simple questions (answer directly)

## Basic Claude Code Commands

### Check Installation
```bash
claude --version
claude --help
```

### Execute Task
```bash
# Non-interactive mode (for automation)
claude -p "Your task description here" --output-format json

# Continue previous session
claude -c -p "Continue from last task" --output-format json

# With specific permission mode
claude -p "Task description" --permission-mode plan --output-format json
```

## Delegation Workflow

### 1. Task Assessment
- Is task complex enough to benefit from Claude's capabilities?
- Does `claude` command exist? (`which claude`)
- What working directory is needed?
- Should this be handled directly instead?

### 2. Command Construction
```bash
# Basic pattern
claude -p "Clear task description with necessary context" --output-format json

# Example: Code review
claude -p "Review the src/auth/ directory for security vulnerabilities and code quality issues" --output-format json

# Example: Architecture design
claude -p "Design a caching layer for this API that handles 10k RPS" --output-format json
```

### 3. Execute and Parse
```bash
# Execute via Bash tool
result=$(claude -p "Task description" --output-format json 2>&1)

# Check exit code (0 = success)
echo $?
```

### 4. Extract Results
Parse JSON output to extract Claude's response. The JSON structure contains:
- `content`: The main response text
- `tool_calls`: Any tool calls made
- `usage`: Token usage statistics

## Output Parsing

### JSON Output Structure
```json
{
  "content": [
    {
      "type": "text",
      "text": "The main response..."
    }
  ],
  "tool_calls": [...],
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 567
  }
}
```

### Key Sections to Extract
1. **Content array**: Claude's text responses
2. **Tool calls**: What tools were invoked
3. **Usage**: Token consumption statistics

## Examples

### Example 1: Code Review
```bash
claude -p "Review the authentication module in src/auth/ for security vulnerabilities, code quality issues, and best practice violations. Provide specific recommendations." --output-format json
```

### Example 2: Architecture Design
```bash
claude -p "Design a caching layer for a REST API that needs to handle 10,000 requests per second with sub-10ms latency. Consider Redis, in-memory, and CDN options." --output-format json
```

### Example 3: Multi-file Refactoring
```bash
claude -p "Refactor the user management system to use dependency injection instead of global state. This spans src/users/, src/auth/, and src/database/ directories." --output-format json
```

### Example 4: Test Generation
```bash
claude -p "Generate comprehensive unit tests for the PaymentProcessor class in src/payments/processor.py, including edge cases, error conditions, and mock dependencies." --output-format json
```

### Example 5: Documentation Generation
```bash
claude -p "Generate comprehensive API documentation for the REST endpoints in src/api/, including request/response schemas, authentication requirements, and example usage." --output-format json
```

## Best Practices

### Clear Task Definitions
- Be specific: "Review src/auth/ for security vulnerabilities"
- Include paths: "In directory /path/to/project, analyze X"
- Specify scope: "Focus on performance bottlenecks in database queries"

### Error Handling
- Check exit code: `if [ $? -eq 0 ]; then ...`
- Parse JSON errors from output
- Have fallback: handle task directly if Claude fails

### Cost Awareness
- Monitor token usage in `usage` field
- Use for tasks where Claude's capabilities justify the cost
- Consider caching strategies for similar queries

## Security Considerations

### Claude Code Safety Features
- **Permission Modes**: `--permission-mode` flag controls approval requirements:
  - `default`: Standard permission prompts
  - `plan`: Approve the overall plan, then individual tool uses
  - `acceptEdits`: Automatically accept file edits
  - `dontAsk`: Minimal prompting (use with caution)
  - `bypassPermissions`: Skip all permissions (dangerous)

- **Tool Control**: `--allowed-tools` and `--disallowed-tools` restrict available tools
- **Output Format**: `--output-format json` for programmatic processing
- **Working Directory**: Uses current directory; use `cd` to change scope

### Risk Mitigation Strategies

1. **Permission Mode Selection**
   ```bash
   # For read-only analysis (safer)
   claude -p "Analyze code structure" --permission-mode default --output-format json

   # For planned operations
   claude -p "Refactor module" --permission-mode plan --output-format json

   # Avoid for sensitive operations
   # ❌ DON'T: claude -p "Task" --permission-mode bypassPermissions
   ```

2. **Tool Restriction**
   ```bash
   # Limit available tools for safer execution
   claude -p "Read-only analysis" --disallowed-tools "Write,Edit" --output-format json

   # Or explicitly allow only read tools
   claude -p "Analysis task" --allowed-tools "Read,Bash(ls:*)" --output-format json
   ```

3. **Working Directory Isolation**
   ```bash
   # Change to specific directory before execution
   cd /safe/workspace && claude -p "Task" --output-format json

   # Use with timeout for safety
   timeout 60 claude -p "Task" --output-format json
   ```

4. **Content Safety**
   - Review prompts for sensitive data exposure
   - Check output for accidental credential leaks
   - Use dedicated workspace directories
   - Implement audit logging for compliance

### Risk-Based Task Categorization

| Risk Level | Task Type | Safety Measures |
|------------|-----------|-----------------|
| **Low** | Read-only analysis, documentation review | `--permission-mode default` |
| **Medium** | Code suggestions, test generation | `--permission-mode plan` |
| **High** | File modifications, refactoring | `--disallowed-tools Write,Edit` or manual review |
| **Critical** | System changes, deployments | Handle directly with oversight |

### Emergency Response
If Claude starts executing dangerous operations:
1. **Immediate Interrupt**: `Ctrl+C` to stop execution
2. **Check Git Status**: `git status` to see file changes
3. **Restore Files**: `git checkout -- .` to revert modifications
4. **Review Logs**: Check session history for executed operations
5. **Adjust Settings**: Strengthen permission modes or tool restrictions

### Recommended Safety Configuration
```bash
# For routine analysis tasks (low risk)
claude -p "Analyze code structure" --permission-mode default --output-format json

# For development tasks (medium risk)
claude -p "Refactor function" --permission-mode plan --output-format json

# For high-risk operations
claude -p "Modify critical files" --permission-mode default --disallowed-tools "Write,Edit,Bash(rm:*)" --output-format json
```

## Integration Pattern

```bash
# Pseudo-implementation for delegation
delegate_to_claude() {
    local task="$1"
    local workdir="${2:-.}"

    if ! command -v claude &> /dev/null; then
        echo "Claude Code not found, handling task directly"
        return 1
    fi

    echo "Delegating to Claude Code: $task"
    output=$(cd "$workdir" && claude -p "$task" --output-format json 2>&1)

    if [ $? -eq 0 ]; then
        # Extract content from JSON
        echo "$output" | jq -r '.content[0].text // empty'
        return 0
    else
        echo "Claude Code failed, fallback to direct handling"
        return 1
    fi
}
```

## Troubleshooting

### Claude Not Found
```bash
# Check installation
which claude

# Expected: /usr/local/bin/claude or similar
# If missing, install via official installer
```

### Permission Issues
```bash
# Check permission mode settings
claude -p "Test" --permission-mode default --output-format json

# Review available permission modes
claude --help | grep permission
```

### Output Parsing Issues
```bash
# Test JSON output
claude -p "Say hello" --output-format json | jq .

# Install jq if needed
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS
```

## References

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Skills Guide](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Anthropic API Documentation](https://docs.anthropic.com/en/api/overview)

---

**Usage**: When you encounter a task that matches the "Suitable Task Examples", delegate it to Claude Code using the patterns above. This creates an efficient subagent workflow where complex tasks are handled by Claude, freeing you for other work.
