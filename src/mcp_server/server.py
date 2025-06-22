"""
FastMCP Echo Server
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import tempfile
import os
import json

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text


@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"


@mcp.resource("echo://{text}")
def echo_template(text: str) -> str:
    """Echo the input text"""
    return f"Echo: {text}"


@mcp.prompt("echo")
def echo_prompt(text: str) -> str:
    return text


@mcp.tool("When you need to shallow clone a Git repository, optionally limiting to a specific folder and its descendants, then read its system prompt and agent config and run Codex CLI accordingly.")
def clone_and_write_prompt(repository: str, request: str, folder: str = "/") -> str:
    """Clone the repo, read system prompt & agent config, then call codex CLI."""
    temp_dir = tempfile.mkdtemp()
    try:
        # shallow sparse clone only necessary data
        subprocess.check_call(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", repository, temp_dir])
        # include only the specified folder if not root
        if folder not in ('', '/'):
            subprocess.check_call(["git", "-C", temp_dir, "sparse-checkout", "set", folder.lstrip('/')])
    except subprocess.CalledProcessError as e:
        return f"Failed to clone {repository}: {e}"
    # Determine working directory inside clone
    work_dir = temp_dir if folder in ('', '/') else os.path.join(temp_dir, folder.lstrip('/'))
    # Read system prompt
    system_path = os.path.join(work_dir, ".agent", "system.md")
    try:
        with open(system_path, "r") as f:
            system_prompt = f.read()
    except Exception as e:
        return f"Failed reading system prompt: {e}"
    # Read agent config for modelId
    agent_json = os.path.join(work_dir, ".agent", "agent.json")
    try:
        with open(agent_json, "r") as f:
            config = json.load(f)
        model_id = config.get("modelId")
    except Exception as e:
        return f"Failed reading agent config: {e}"
    if not model_id:
        return "modelId not found in agent.json"

    # Call codex CLI
    try:
        output = subprocess.check_output(["codex", "--model", model_id, request], cwd=work_dir, text=True)
    except subprocess.CalledProcessError as e:
        return f"Codex CLI failed: {e}"
    return output


def main():
    """Entry point for the MCP server"""
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def run_server():
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
