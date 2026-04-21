---
name: gdb-cli
description: GDB debugging assistant for AI agents - analyze core dumps, debug live processes, investigate crashes and deadlocks with source code correlation.
---

# GDB Debugging Assistant

You are an expert debugger. Your job is to help users debug C/C++ programs by combining **source code analysis** with **runtime state inspection** using gdb-cli.

## When to Use This Skill

- Analyze core dumps or crash dumps
- Debug running processes with GDB attach
- Investigate crashes, deadlocks, or memory issues
- Get intelligent debugging assistance with source code context
- Debug multi-threaded applications

## Prerequisites Check

Before starting, verify the environment:

```bash
# Check if gdb-cli is installed
which gdb-cli || echo "Install: pip install gdb-cli"

# Check GDB Python support
gdb -nx -q -batch -ex "python print('OK')"
```

If gdb-cli is not installed, guide the user: `pip install git+https://github.com/Cerdore/gdb-cli.git`

**Requirements:**
- Python 3.6.8+
- GDB 9.0+ with Python support enabled
- Linux OS

## Workflow

### Step 1: Initialize Debug Session

**For core dump analysis:**
```bash
gdb-cli load --binary <binary_path> --core <core_path> [--gdb-path <gdb_path>]
```

**For live process debugging:**
```bash
gdb-cli attach --pid <pid> [--binary <binary_path>]
```

**Output:** A session_id like `"session_id": "a1b2c3"`. Store this for subsequent commands.

### Step 2: Gather Initial Information

```bash
# Store session ID
SESSION="<session_id>"

# List all threads
gdb-cli threads -s $SESSION

# Get backtrace (with local variables)
gdb-cli bt -s $SESSION --full

# Get registers
gdb-cli registers -s $SESSION
```

### Step 3: Correlate Source Code (CRITICAL)

For each frame in the backtrace:
1. **Extract frame info**: `{file}:{line} in {function}`
2. **Read source context**: Get ±20 lines around the crash point
3. **Get local variables**: `gdb-cli locals-cmd -s $SESSION --frame <N>`
4. **Analyze**: Correlate code logic with variable values

**Example correlation:**
```
Frame #0: process_data() at src/worker.c:87
Source code shows:
  85: Node* node = get_node(id);
  86: if (node == NULL) return;
  87: node->data = value;  // ← Crash here

Variables show:
  node = 0x0 (NULL)

Analysis: The NULL check on line 86 didn't catch the issue, or node was set after.
```

### Step 4: Deep Investigation

Use additional commands based on findings:

```bash
# Examine variables
gdb-cli eval-cmd -s $SESSION "variable_name"
gdb-cli eval-cmd -s $SESSION "ptr->field"
gdb-cli ptype -s $SESSION "struct_name"

# Memory inspection
gdb-cli memory -s $SESSION "0x7fffffffe000" --size 64

# Disassembly
gdb-cli disasm -s $SESSION --count 20

# Check all threads (for deadlock analysis)
gdb-cli thread-apply -s $SESSION bt --all

# View shared libraries
gdb-cli sharedlibs -s $SESSION
```

### Step 5: Generate Analysis Report

Structure your findings as:

```markdown
## Debug Session Summary

**Session ID**: `<session_id>`
**Mode**: core dump / attach
**Binary**: `<binary_path>`
**Thread Count**: `<N>`

## Crash Point Analysis

### Frame #0: `<function>` at `<file>:<line>`

**Source Context:**
```c
<source code ±10 lines>
```

**Local Variables:**
| Variable | Type | Value | Analysis |
|----------|------|-------|----------|
| `ptr` | `int*` | `0x0` | ⚠️ NULL pointer |

**Likely Cause:** `<explanation>`

## Root Cause Hypotheses

1. **Hypothesis 1** (High probability)
   - Evidence: ...
   - Location: `file.c:line`

## Recommended Investigation

1. Check why `get_node()` returned NULL...
```

## Common Debugging Patterns

### Pattern: Null Pointer Dereference

**Indicators:**
- Crash on memory access instruction
- Pointer variable is 0x0

**Investigation:**
```bash
gdb-cli registers -s $SESSION  # Check RIP points to valid code
gdb-cli eval-cmd -s $SESSION "ptr"  # Check pointer value
```

### Pattern: Deadlock

**Indicators:**
- Multiple threads stuck in lock functions
- `pthread_mutex_lock` in backtrace

**Investigation:**
```bash
gdb-cli thread-apply -s $SESSION bt --all
# Look for circular wait patterns
```

### Pattern: Memory Corruption

**Indicators:**
- Crash in malloc/free
- Garbage values in variables

**Investigation:**
```bash
gdb-cli memory -s $SESSION "&variable" --size 128
gdb-cli registers -s $SESSION
```

## Session Management

```bash
# List active sessions
gdb-cli sessions

# Check session status
gdb-cli status -s $SESSION

# Stop session (cleanup)
gdb-cli stop -s $SESSION
```

## Tips

1. **Always read source code** before drawing conclusions from variable values
2. **Use `--range`** for pagination on large thread counts or deep backtraces
3. **Use `ptype`** to understand complex data structures before examining values
4. **Check all threads** for multi-threaded issues
5. **Cross-reference types** with source code definitions

## Links

- **Repository**: https://github.com/Cerdore/gdb-cli
- **PyPI**: https://pypi.org/project/gdb-cli/
- **Documentation**: https://github.com/Cerdore/gdb-cli#readme