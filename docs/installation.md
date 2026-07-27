# Installation

## Quick install

```bash
pip install scvi-tools-mcp
```

or with `uvx` (no install needed, runs directly):

```bash
uvx scvi-tools-mcp
```

## MCP client configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scvi-tools": {
      "command": "uvx",
      "args": ["scvi-tools-mcp"]
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add scvi-tools-mcp -s user -- uvx scvi-tools-mcp
```

### OpenAI Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.scvi-tools-mcp]
command = "uvx"
args   = ["scvi-tools-mcp"]
```

### Cursor / Windsurf / other MCP clients

```json
{ "command": "uvx", "args": ["scvi-tools-mcp"] }
```

## Optional: scvi-tools runtime

The server itself does not require `scvi-tools`. Install it only if you want to run the
knowledge refresh scripts locally:

```bash
pip install "scvi-tools-mcp[scvi]"
```

## Development install

```bash
git clone https://github.com/Yoseflab/scvi-tools-mcp
cd scvi-tools-mcp
pip install -e . --group dev
pre-commit install
pytest
```

## Requirements

- Python 3.12, 3.13, or 3.14
- fastmcp ≥ 3.0
- pydantic ≥ 2.0
