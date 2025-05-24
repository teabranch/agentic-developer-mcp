# Codex MCP Wrapper

This project wraps OpenAI's Codex CLI as an MCP (Model Context Protocol) server, making it accessible through the TeaBranch/open-responses-server middleware.

## Requirements

- Node 22 (`nvm install 22.15.1 | nvm use 22.15.1`) required for Codex

## Overview

The setup consists of three main components:

1. **Codex CLI**: OpenAI's command-line interface for interacting with Codex.
2. **MCP Wrapper Server**: A Node.js Express server that forwards MCP requests to Codex CLI and formats responses as MCP.
3. **open-responses-server**: A middleware service that provides Responses API compatibility and MCP support.

## Installation

### Using Docker (Recommended)

```bash
# Clone this repository
git clone https://github.com/yourusername/codex-mcp-wrapper.git
cd codex-mcp-wrapper

# Start the services
./start.sh
```

This will start:
- Codex MCP wrapper on port 8080
- open-responses-server on port 3000

### Manual Installation

```bash
# Install dependencies
npm install

# Install Codex CLI globally
npm install -g @openai/codex

# Start the MCP server
node mcp-server.js
# Install the package in development mode
pip install -e .
```

## Usage

You can run the MCP server using either stdio or SSE transport:

```bash
# Using stdio (default)
python -m mcp_server

# Using SSE on a specific port
python -m mcp_server --transport sse --port 8000
```

## Tool Documentation

### run_codex

Clones a repository, checks out a specific branch (optional), navigates to a specific folder (optional), and runs Codex with the given request.

#### Parameters

- `repository` (required): Git repository URL
- `branch` (optional): Git branch to checkout
- `folder` (optional): Folder within the repository to focus on
- `request` (required): Codex request/prompt to run

#### Example

```json
{
  "repository": "https://github.com/username/repo.git",
  "branch": "main",
  "folder": "src",
  "request": "Analyze this code and suggest improvements"
}
```

## Development

This project uses the MCP Python SDK to implement an MCP server. The primary implementation is in `mcp_server/server.py`.

## License

MIT
