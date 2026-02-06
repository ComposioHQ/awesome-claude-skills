---
name: python-venv
description: "Before running Python scripts or installing packages, you MUST use a virtual environment in the current working directory. This applies to: running .py files, using pip/uv pip install, or any task requiring third-party packages. Exceptions: simple one-liners using only Python standard library."
---

# Python Virtual Environment Requirement

## Core Rule

**Use virtual environment when installing packages or running scripts that require third-party dependencies.**

## When Virtual Environment is REQUIRED

| Scenario | Required? | Reason |
|----------|-----------|--------|
| `pip install` / `uv pip install` | ✅ YES | Installing packages |
| Running `.py` files with third-party imports | ✅ YES | Needs dependencies |
| `python script.py` with `requirements.txt` | ✅ YES | Project dependencies |
| Multi-file Python projects | ✅ YES | Isolation needed |

## When Virtual Environment is NOT Required

| Scenario | Required? | Example |
|----------|-----------|---------|
| Simple one-liner with stdlib only | ❌ NO | `python3 -c "print('hello')"` |
| Quick math/string operations | ❌ NO | `python3 -c "print(2**10)"` |
| Using only built-in modules | ❌ NO | `python3 -c "import json; ..."` |
| Checking Python version | ❌ NO | `python3 --version` |

### Python Standard Library (No venv needed)

These modules are built-in and don't require virtual environment:
```
os, sys, json, re, math, datetime, pathlib, subprocess, 
collections, itertools, functools, argparse, logging,
urllib, http, socket, threading, multiprocessing, etc.
```

## Workflow (When venv IS Required)

```
1. Check if virtual environment exists (.venv, venv, env, .env) → If YES, activate and reuse it
2. If NOT exists → Create with uv (if available) or python3 -m venv
3. Activate, then proceed with Python commands
```

## Detecting Existing Virtual Environment

Check in this order (first match wins):
```bash
# Common virtual environment directory names
.venv/  →  Most common (preferred)
venv/   →  Also common
env/    →  Sometimes used
.env/   →  Less common (be careful: may conflict with dotenv files)
```

## Setup Methods

### Option 1: uv (Recommended - Faster)

```bash
# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Install packages
uv pip install <package>
```

### Option 2: Standard venv (Fallback if uv not installed)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Install packages
pip install <package>
```

### Option 3: Conda/Mamba

```bash
# Create environment
conda create -n myenv python=3.11

# Activate
conda activate myenv

# Install packages
conda install <package>
# or
pip install <package>
```

## Workflow Checklist

Before Python operations requiring venv:

1. [ ] Check for existing virtual environment (in order): `.venv/`, `venv/`, `env/`, `.env/`
2. [ ] Also check for conda: `conda info --envs` or check if `CONDA_PREFIX` is set
3. [ ] If exists → **Reuse it** (activate the found environment)
4. [ ] If not exists → Create: `uv venv` (preferred) or `python3 -m venv .venv` (fallback)
5. [ ] Activate and proceed

**Priority: Always reuse existing virtual environment to preserve installed packages.**

## Quick Reference

| Task | Linux/macOS | Windows |
|------|-------------|---------|
| Create venv (uv) | `uv venv` | `uv venv` |
| Create venv (standard) | `python3 -m venv .venv` | `python -m venv .venv` |
| Activate | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Install package (uv) | `uv pip install <pkg>` | `uv pip install <pkg>` |
| Install package (pip) | `pip install <pkg>` | `pip install <pkg>` |
| Install from requirements | `uv pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Install from pyproject.toml | `uv pip install -e .` | `uv pip install -e .` |
| Deactivate | `deactivate` | `deactivate` |
| Conda activate | `conda activate <env>` | `conda activate <env>` |

## Common Patterns

### Standard Pattern (Linux/macOS) - Reuse or Create with Fallback
```bash
# Find existing venv or create new one (uv with fallback to venv)
if [ -d .venv ]; then
    source .venv/bin/activate
elif [ -d venv ]; then
    source venv/bin/activate
elif [ -d env ]; then
    source env/bin/activate
elif command -v uv &> /dev/null; then
    uv venv && source .venv/bin/activate
else
    python3 -m venv .venv && source .venv/bin/activate
fi
```

### One-liner (Linux/macOS)
```bash
# Quick version: check .venv, fallback to create
[ -d .venv ] && source .venv/bin/activate || { command -v uv &>/dev/null && uv venv || python3 -m venv .venv; source .venv/bin/activate; }
```

### Windows PowerShell
```powershell
# Find existing venv or create new one
if (Test-Path .venv) { .\.venv\Scripts\Activate.ps1 }
elseif (Test-Path venv) { .\venv\Scripts\Activate.ps1 }
elseif (Get-Command uv -ErrorAction SilentlyContinue) { uv venv; .\.venv\Scripts\Activate.ps1 }
else { python -m venv .venv; .\.venv\Scripts\Activate.ps1 }
```

### Running a Python Script
```bash
# Activate existing or create new
[ -d .venv ] && source .venv/bin/activate || { command -v uv &>/dev/null && uv venv || python3 -m venv .venv; source .venv/bin/activate; }

# Install dependencies (check both requirements.txt and pyproject.toml)
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ] && pip install -e .

# Run script
python script.py
```

### Check if venv is Active
```bash
# Should show path containing .venv, venv, or env
which python

# Or check VIRTUAL_ENV environment variable
echo $VIRTUAL_ENV
```

### Check if Conda Environment is Active
```bash
# Check CONDA_PREFIX
echo $CONDA_PREFIX

# List all conda environments
conda info --envs
```

## Forbidden Actions

- Using `pip install` with system Python (always use venv)
- Installing packages globally
- Assuming third-party packages are available without explicit installation
- Overwriting existing virtual environment without checking first

## Allowed Without venv

- `python3 -c "print('hello')"`
- `python3 -c "import os; print(os.getcwd())"`
- `python3 --version`
- Any stdlib-only one-liner

## Project Type Detection

| File Present | Project Type | Install Command |
|--------------|--------------|-----------------|
| `requirements.txt` | Traditional | `pip install -r requirements.txt` |
| `pyproject.toml` | Modern (PEP 517/518) | `pip install -e .` or `uv pip install -e .` |
| `pyproject.toml` + `poetry.lock` | Poetry | `poetry install` |
| `pyproject.toml` + `uv.lock` | uv native | `uv sync` |
| `setup.py` | Legacy | `pip install -e .` |
| `Pipfile` | Pipenv | `pipenv install` |
| `environment.yml` | Conda | `conda env create -f environment.yml` |

## Troubleshooting

### Corrupted Virtual Environment

If venv is broken (import errors, missing packages after install):

```bash
# Remove and recreate
rm -rf .venv
uv venv && source .venv/bin/activate
# or
python3 -m venv .venv && source .venv/bin/activate
```

### Wrong Python Version

```bash
# Specify Python version with uv
uv venv --python 3.11

# Or with standard venv
python3.11 -m venv .venv
```

### Permission Denied on Windows

Run PowerShell as Administrator, or:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### WSL (Windows Subsystem for Linux)

Use Linux commands in WSL:
```bash
# Same as Linux/macOS
source .venv/bin/activate
```

Note: Don't mix Windows venv with WSL. Create separate venv for each environment.
