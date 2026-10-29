# MCP integration

OpenTruth uses the official Python MCP SDK and defaults to stdio. Start it with:

```sh
opentruth --workspace /absolute/allowed/workspace mcp
```

For clients supporting the common local server configuration shape (check your client's current
settings), supply the absolute executable and workspace:

```json
{
  "mcpServers": {
    "opentruth": {
      "command": "/absolute/OpenTruth/.venv/bin/opentruth",
      "args": ["--workspace", "/absolute/allowed/workspace", "mcp"]
    }
  }
}
```

Ten tools: register_source, add_claim, link_evidence, search_claims, inspect_claim,
check_conflicts, get_claim_history, review_claim, export_evidence, verify_sources. Inputs have SDK-generated
schemas and structured results. Invalid operations produce MCP errors with sanitized messages;
stdout is reserved for protocol traffic. File inputs are workspace-relative. The authorized
workspace is an access boundary, not an OS sandbox; run with an appropriate OS account.

`python -m pytest tests/test_interfaces.py -k real_mcp` tests initialize, list_tools, and actual
tool calls using ClientSession and stdio_client against a subprocess. Direct function calls alone
are not interoperability evidence.

ChatGPT compatibility is NOT VERIFIED. This package provides no remote HTTPS MCP transport,
connector registration, or authentication. Do not paste local stdio configuration into ChatGPT
and assume it works. Consult current official ChatGPT connector requirements before deploying a
separate remote bridge; none is implemented or recommended as a verified v0.1 integration.
SDK reference: https://github.com/modelcontextprotocol/python-sdk .

`verify_sources` checks local file byte integrity only; it never promotes scientific source verification.
Backup and restore are local Python/CLI operations, not MCP tools. `add_claim` accepts optional
`context_template` checklists; see [context templates](context-templates.md).
