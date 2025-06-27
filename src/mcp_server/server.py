"""
FastMCP Agentic Developer MCP Server
"""

from fastmcp import FastMCP
import subprocess
import tempfile
import os
import json

# Create server
mcp = FastMCP("Agentic Developer MCP Server")


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


@mcp.tool("operate-developer")
def clone_and_write_prompt(repository: str, request: str, folder: str = "/") -> str:
    """When you need to shallow clone a Git repository, optionally limiting to a specific folder and its descendants, then read its system prompt and agent config and run Codex CLI accordingly."""
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
    """Main entry point that supports command line arguments"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Agentic Developer MCP Server')
    parser.add_argument('--transport', choices=['stdio', 'sse', 'http'], default='stdio', help='Transport type')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    
    args = parser.parse_args()
    
    if args.transport == 'sse':
        mcp.run(transport="sse", host=args.host, port=args.port)
    elif args.transport == 'http':
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()
