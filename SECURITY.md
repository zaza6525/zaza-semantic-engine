# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 3.x.x   | ✅ Yes    |
| 2.x.x   | ❌ No     |

## Reporting a Vulnerability

**Do not open public issues for security vulnerabilities.**

Instead, report them privately:

1. Open a [GitHub Security Advisory](https://github.com/zaza6525/zaza-semantic-engine/security/advisories/new)
2. Or contact the maintainer directly via email or private message.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

I'll acknowledge receipt within 48 hours and work on a fix as soon as possible.

## Security considerations

Zaza Semantic Engine processes files from the filesystem. By design:

- **Files are read locally** — no documents are sent over the network.
- **The API server binds to `127.0.0.1` by default** — it is not exposed externally.
- **Upload endpoints** use temporary directories with restricted permissions.

### Known risk areas

- **File upload via API** (`/ingest/file`, `/ingest/directory`): validates file type and size limits. Do not expose the API to untrusted networks.
- **PDF/DOCX parsing**: relies on `pypdf` and `python-docx`. Keep them updated to avoid known parsing vulnerabilities.
- **Arbitrary paths**: `zaza ingest <path>` reads from any accessible directory. Use with caution in multi-user environments.

## Dependencies

Run this to audit your installed dependencies:

```bash
pip install safety
safety check
```
