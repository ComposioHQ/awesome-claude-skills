# Enterprise-Level Contribution Practices

Large foundations have rigorous standards that make you a better contributor everywhere.

## Linux Kernel

The most demanding contribution standards in open source.

### Patch Format

```
[PATCH] subsystem: summary phrase (max 70-75 chars)

Detailed explanation of what the patch does and why.
Wrap at 75 characters.

Signed-off-by: Your Name <email@example.com>
```

### Key Requirements

- **Signed-off-by required**: Certifies you have the right to submit (Developer Certificate of Origin)
- **Plain text only**: "No MIME, no links, no compression, no attachments"
- **Use `git send-email`**: Patches submitted via email, not pull requests
- **One logical change per patch**: Kernel must build and run after each patch
- **Run `scripts/checkpatch.pl`**: Style-check before submission

### Tags

| Tag | Meaning |
|-----|---------|
| `Acked-by:` | Developer agrees the patch is appropriate |
| `Reviewed-by:` | Developer has reviewed for correctness |
| `Tested-by:` | Person has tested and verified it works |
| `Reported-by:` | Credits the bug reporter |
| `Fixes:` | References the commit that introduced the bug |

### Finding Maintainers

```bash
scripts/get_maintainer.pl <patch-file>
```

### Review Process

- Wait 1-2 weeks before following up
- Use inline replies (not top-posting)
- Remove Acked-by/Tested-by tags if patch changes substantially
- Include changelog between patch versions

## Apache Software Foundation

### Progression Path

```
User → Contributor → Committer → PMC Member
```

### Key Requirements

- **Contributor License Agreement (CLA)**: Required before contributions accepted
- **Mailing list communication**: Use `dev@project.apache.org` for discussions
- **Apache License 2.0**: All contributions fall under this license

### What Apache Values

- Contributions beyond code: documentation, design, event coordination
- Long-term commitment over one-off patches
- Consistent, quality contributions lead to committer invitations

## References

- [Linux Kernel - Submitting Patches](https://docs.kernel.org/process/submitting-patches.html)
- [Apache - Get Involved](https://www.apache.org/foundation/getinvolved.html)
