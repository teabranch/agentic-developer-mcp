# Agentic Developer MCP Server

An MCP server implementation that clones a Git repository and runs Codex on its contents.

## Overview

This MCP server provides a tool for cloning a Git repository, optionally checking out a specific branch, focusing on a particular folder, and running Codex with a given request.

## Installation

```bash
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
