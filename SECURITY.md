# Security Policy

## Supported Versions

This repository is a single-file browser application with no versioned
releases. Security fixes are applied to the `main` branch.

| Branch | Supported |
| ------ | --------- |
| `main` | ✅       |

## Reporting a Vulnerability

Please report security issues privately through GitHub's
"Report a vulnerability" feature on this repository's Security tab. Do not
open a public issue for an unfixed vulnerability.

Include the affected file/line, reproduction steps, and the impact you
observed. You can expect an acknowledgement within a week. Once the issue is
confirmed, a fix will be committed to `main` with a commit message describing
the vulnerability; you will be notified when the fix is public. Reports that
are declined will be explained with the reason.

## Scope and design notes

- The application runs entirely in the browser. API mode is opt-in and sends
  data only to an endpoint the user supplies.
- Runtime assets are bundled in `vendor/`. CDN fallbacks are only used with
  Subresource Integrity, and secondary assets must exist locally (fail-closed).
- Optional remote voice downloads are verified against SHA-256 before use or
  caching.
