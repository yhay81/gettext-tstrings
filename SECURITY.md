# Security policy

`gettext-tstrings` treats catalog data as untrusted input at the rendering
boundary. Reports that show a translation can execute Python, bypass placeholder
validation, retain interpolated values unexpectedly, or cause a denial of
service are especially important.

## Supported versions

The latest release on PyPI and the current `main` branch receive security fixes.
Older alpha releases may be fixed only by publishing a new release.

## Report privately

Do not open a public issue for a suspected vulnerability.

Use GitHub's
[private vulnerability reporting](https://github.com/yhay81/gettext-tstrings/security/advisories/new)
form. Include:

- the affected version or commit;
- a minimal reproducer;
- the impact you believe is possible;
- any suggested mitigation;
- whether the report or exploit details have been shared elsewhere.

You will receive an acknowledgement after the report is reviewed. The maintainer
will coordinate validation, a fix, a release, and public disclosure with you.
Please allow time for a patched release before publishing details.

Usage questions, ordinary crashes, and incorrect extraction without a security
impact should use the public bug-report form instead.
