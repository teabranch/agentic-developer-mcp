![image](https://github.com/user-attachments/assets/8afeab98-f30c-4c31-8c11-ab8557c16620)


# Agentic Developer MCP 

This project wraps OpenAI's Codex CLI as an MCP (Model Context Protocol) server, making it accessible through the TeaBranch/open-responses-server middleware.  
This engine may be replaced with OpenCode or Amazon Strands

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

### clone_and_write_prompt

Clones a repository, reads the system prompt from `.agent/system.md`, parses `modelId` from `.agent/agent.json`, writes the request to a `.prompt` file, and invokes the Codex CLI with the extracted model.

#### Parameters

- `repository` (required): Git repository URL
- `request` (required): Prompt text to run through Codex
- `folder` (optional, default `/`): Subfolder within the repository to operate in

#### Example

```json
{
  "repository": "https://github.com/username/repo.git",
  "folder": "src",
  "request": "Analyze this code and suggest improvements"
}
```

### MCPS Configuration

Place a `mcps.json` file under the `.agent/` directory to register available MCP tools. Codex will load this configuration automatically.

Example `.agent/mcps.json`:
```json
{
  "mcpServers": {
    "agentic-developer-mcp": {
      "url": "..."
    }
  }
}
```

## Development

This project uses the MCP Python SDK to implement an MCP server. The primary implementation is in `mcp_server/server.py`.

## License

MIT
