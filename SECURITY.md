# Security policy

v0.1 targets one trusted local OS user. It provides workspace file checks and parameterized SQL,
not authentication, encryption, a hostile-process sandbox, or tamper-proof history.
Do not expose stdio tools to untrusted users with access to a sensitive workspace.

For vulnerabilities use GitHub private vulnerability reporting if enabled; otherwise contact the
repository owner privately using their GitHub profile contact options. Do not post exploit data
or secrets in public issues. Include affected version, minimal synthetic reproduction, impact,
and suggested mitigation. No response-time or private-reporting availability guarantee is made.
See [technical security model](docs/security.md).
