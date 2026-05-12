---
name: secrets-security-scanner
description: Scan codebases for hardcoded secrets, API keys, and environment variable vulnerabilities. Detects leaked credentials in .env files, source code, and git history. Provides secure migration strategies to secret managers. Use when auditing security, before commits, or setting up secure configuration management.
---

# Secrets & Environment Security Scanner

Identify and fix security vulnerabilities related to secrets, API keys, credentials, and environment configuration in your codebase.

## When to Use This Skill

- Scanning for hardcoded secrets or API keys
- Auditing .env files and environment variables
- Checking git history for accidentally committed credentials
- Setting up pre-commit hooks to prevent secret leaks
- Migrating to secret managers (Vault, AWS Secrets Manager, 1Password)
- Comparing configuration across dev/staging/production environments
- Validating security before deployment

## Core Workflows

### Workflow 1: Quick Security Scan

**Execute:**

```bash
# Check if .env is tracked in git (critical issue)
git ls-files | grep -E "^\.env$"

# Scan for common secret patterns
grep -r -i -n -E "(api[_-]?key|secret[_-]?key|password|token|access[_-]?key)" \
  --include="*.js" --include="*.py" --include="*.java" --include="*.go" \
  --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=dist .

# Check for hardcoded credentials (specific patterns)
grep -r -n -E "(AKIA[0-9A-Z]{16}|ghp_[0-9a-zA-Z]{36}|sk-[a-zA-Z0-9]{48})" \
  --exclude-dir=node_modules --exclude-dir=venv .

# Verify .env is in .gitignore
grep "^\.env$" .gitignore || echo "WARNING: .env not in .gitignore"
```

**Report findings with:**
- Files containing potential secrets
- Specific line numbers and patterns matched
- Risk level (Critical/High/Medium/Low)
- Recommended fixes for each issue

---

### Workflow 2: Git History Secret Scan

**Execute:**

```bash
# Check if .env files were ever committed
git log --all --full-history -- "*.env"

# Search git history for AWS keys
git log --all -p -S "AKIA" --pretty=format:"%h %an %ad - %s"

# Search for API keys in history
git log --all -p -S "api_key" -S "secret" --pretty=format:"%h %an %ad"
```

**If secrets found in history:**
1. Immediately rotate all exposed credentials
2. Consider git history rewrite using BFG Repo-Cleaner
3. Notify team about compromised credentials
4. Update security procedures

---

### Workflow 3: Environment File Security Audit

**Execute:**

```bash
# Find all .env files
find . -name ".env*" -type f -not -path "*/node_modules/*"

# Validate .gitignore coverage
for pattern in ".env" ".env.local" ".env.*.local"; do
  grep -q "^${pattern}$" .gitignore && echo "$pattern: protected" || echo "$pattern: EXPOSED"
done

# Analyze .env structure
if [ -f .env ]; then
  echo "Total variables: $(grep -v "^#" .env | grep -v "^$" | wc -l)"
  echo "Potential secrets: $(grep -iE "(password|secret|key|token)" .env | wc -l)"
fi
```

**Report:**
- Which .env files are tracked/ignored
- Missing .gitignore patterns
- Variables that should be secrets vs config
- Recommendations for .env.example template

---

### Workflow 4: Setup Pre-Commit Secret Detection

**Install tools:**

```bash
# Install pre-commit framework
pip install pre-commit

# Install gitleaks
brew install gitleaks  # macOS
```

**Create .pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks
        name: Detect hardcoded secrets
        entry: gitleaks protect --verbose --redact --staged
        language: system

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=500']
```

**Activate:**

```bash
pre-commit install
pre-commit run --all-files
```

---

### Workflow 5: Migrate to Secret Manager

**Recommended solutions based on infrastructure:**

**AWS Infrastructure:**
- Use AWS Secrets Manager ($0.40/secret/month)
- Automatic rotation for RDS, Redshift
- IAM-based access control

**Multi-cloud or On-premise:**
- Use HashiCorp Vault (open source)
- Self-hosted option available
- Advanced features for enterprises

**Small Teams:**
- Use 1Password ($7.99/user/month)
- Easy to use, team sharing
- CLI and API access

**Open Source:**
- Use Infisical (free, self-hosted)
- Modern UI, good developer experience
- Kubernetes integration

**Migration code example (AWS Secrets Manager):**

```python
import boto3
import json

def migrate_to_aws_secrets():
    client = boto3.client('secretsmanager', region_name='us-east-1')

    secrets = {
        'myapp/database': {
            'host': 'db.example.com',
            'password': 'actual_password_here',
            'username': 'dbuser'
        },
        'myapp/api-keys': {
            'openai': 'sk-...',
            'stripe': 'sk_live_...'
        }
    }

    for name, value in secrets.items():
        client.create_secret(
            Name=name,
            SecretString=json.dumps(value),
            Tags=[{'Key': 'Environment', 'Value': 'production'}]
        )

def retrieve_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

---

## Common Secret Patterns Detected

| Secret Type | Pattern | Risk Level |
|------------|---------|-----------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | Critical |
| GitHub Token | `ghp_[0-9a-zA-Z]{36}` | Critical |
| OpenAI API Key | `sk-[a-zA-Z0-9]{48}` | Critical |
| Stripe Secret | `sk_live_[0-9a-zA-Z]{24}` | Critical |
| JWT Token | `eyJ[A-Za-z0-9_-]*\.` | High |
| Generic API Key | `api[_-]?key.*['"][^'"]{16,}` | High |
| Database URL | `postgres://.*:.*@` | High |
| Private Key | `-----BEGIN.*PRIVATE KEY-----` | Critical |

---

## Security Best Practices

### Secure Secret Management

**1. Use environment variables correctly:**
```bash
# In .env (never commit!)
DATABASE_URL=postgres://user:pass@localhost/db
API_KEY=your_key_here

# In code
const apiKey = process.env.API_KEY;
```

**2. Proper .gitignore setup:**
```gitignore
.env
.env.local
.env.*.local
.env.development.local
.env.test.local
.env.production.local
*.env.backup
```

**3. Generate strong secrets:**
```bash
# 256-bit random secret
openssl rand -hex 32

# Base64 encoded
openssl rand -base64 32
```

### What NOT to Do

**Never hardcode secrets:**
```javascript
// BAD
const apiKey = "sk-1234567890";

// GOOD
const apiKey = process.env.API_KEY;
```

**Never commit .env files:**
```bash
# BAD
git add .env

# GOOD
git add .env.example
```

**Never use weak secrets:**
```bash
# BAD
JWT_SECRET=secret

# GOOD
JWT_SECRET=a3d8f7e9c1b4d6a8f2e5c9b7d3a6f8e1b4c7d2a9f5e8b1c4d7a3f6e9b2c5d8a1
```

---

## Secret Manager Comparison

| Solution | Cost | Auto Rotation | Self-Hosted | Best For |
|----------|------|---------------|-------------|----------|
| AWS Secrets Manager | $0.40/secret/month | Yes | No | AWS users |
| HashiCorp Vault | Free (OSS) | Yes | Yes | Enterprises |
| 1Password | $7.99/user/month | No | No | Small teams |
| Infisical | Free | Yes | Yes | Developers |

---

## CI/CD Integration

**GitHub Actions:**
```yaml
name: Secret Scan
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gitleaks/gitleaks-action@v2
```

**GitLab CI:**
```yaml
secret-scan:
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --verbose --no-git
```

---

## Quick Reference

```bash
# Scan for secrets
grep -r -E "(api[_-]?key|secret|password)" --include="*.js" .

# Check .env in git
git ls-files | grep "\.env"

# Search git history
git log --all -p -S "api_key"

# Install pre-commit
pip install pre-commit && pre-commit install

# Generate strong secret
openssl rand -hex 32

# Find all .env files
find . -name ".env*" -type f
```

---

## Resources

### Secret Management Tools
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) - AWS native secrets management
- [HashiCorp Vault](https://www.vaultproject.io/) - Open-source secrets manager
- [1Password](https://developer.1password.com/) - Team password manager
- [Infisical](https://infisical.com/) - Open-source secret platform

### Security Scanners
- [Gitleaks](https://github.com/gitleaks/gitleaks) - Fast secret scanner
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Git history scanner
- [git-secrets](https://github.com/awslabs/git-secrets) - AWS secret prevention
- [detect-secrets](https://github.com/Yelp/detect-secrets) - Yelp scanner

### Best Practice Guides
- [GitGuardian: Environment Security](https://blog.gitguardian.com/secure-your-secrets-with-env/)
- [Beyond .env Files](https://medium.com/@instatunnel/beyond-env-files-the-new-best-practices-for-managing-secrets-in-development-b4b05e0a3055)
- [Environment Variable Management 2026](https://www.envsentinel.dev/blog/environment-variable-management-tips-best-practices)
- [CyberArk: Environment Variables Security](https://developer.cyberark.com/blog/environment-variables-dont-keep-secrets-best-practices-for-plugging-application-credential-leaks/)

---

## Notes for Claude

**Activation Keywords:** secrets, api keys, credentials, environment, .env, security, scan, audit, vault, secrets manager

**Always:**
- Scan thoroughly before reporting findings
- Use `--redact` flags to hide actual secret values
- Explain risk levels clearly
- Provide actionable fixes with code examples
- Consider user's infrastructure when recommending solutions
- Check git history if secrets found in files

**Never:**
- Display actual secret values in output
- Suggest insecure practices
- Skip .gitignore validation

---

**Inspired by:** Security best practices from [GitGuardian](https://blog.gitguardian.com/), [CyberArk](https://developer.cyberark.com/), and the security research community
