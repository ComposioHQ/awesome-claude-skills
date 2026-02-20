# Reporting Security Vulnerabilities

Security issues require special handling—never open public issues for vulnerabilities.

## Finding the Security Policy

Look for `SECURITY.md` in the repository root, `docs/`, or `.github/` folder.

## Coordinated Disclosure Process

1. **Report privately**: Use project's security contact or GitHub's private vulnerability reporting
2. **Provide details**: Reproduction steps, affected versions, potential impact
3. **Wait for acknowledgment**: Projects typically respond within a few days
4. **Coordinate on timeline**: Standard disclosure window is 90 days
5. **Help with the fix**: Offer to review patches or test fixes
6. **Public disclosure**: After patch is released, details can be published

## Timeline Expectations

| Situation | Timeline |
|-----------|----------|
| Standard vulnerability | 90 days to patch + disclose |
| Actively exploited | Shorter—urgent patching needed |
| Complex fix required | May extend beyond 90 days |

## Vulnerability Report Template

```markdown
## Vulnerability Report

**Affected Component**: [module/package name]
**Affected Versions**: [version range]
**Severity**: [Critical/High/Medium/Low]

## Description
[Clear explanation of the vulnerability]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Observe vulnerability]

## Impact
[What an attacker could do]

## Suggested Fix (optional)
[If you have ideas for remediation]

## Environment
- OS: [e.g., Ubuntu 22.04]
- Version: [e.g., v2.1.0]
```

## After Disclosure

- You may receive credit in the CVE and release notes
- Some projects have bug bounty programs
- Never disclose publicly before the patch is available

## References

- [Google OSS Vulnerability Guide](https://github.com/google/oss-vulnerability-guide)
- [OWASP Vulnerability Disclosure Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html)
