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


@mcp.tool("instruct-developer")
def clone_and_write_prompt(repository: str, request: str, folder: str = "/") -> str:
    """When you need to shallow clone a Git repository, optionally limiting to a specific folder and its descendants, then read its system prompt and agent config and run Codex CLI accordingly."""
    temp_dir = tempfile.mkdtemp()
    try:        # Clean up any existing directory
        if os.path.exists(temp_dir):
            subprocess.check_call(["rm", "-rf", temp_dir])
            
        # normal clone for testing - will optimize later
        subprocess.check_call(["git", "clone", repository, temp_dir])
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
        # Return error message with existing items in the directory
        items = os.listdir(work_dir)
        if not items:
            items = ["(empty directory)"]
        # Return a formatted error message with existing items
        latest_commit = subprocess.check_output(["git", "-C", work_dir, "rev-parse", "HEAD"], text=True).strip()
        return f"Failed reading system prompt: {e}. \n Latest commit: {latest_commit} . \n items ({len(items)}) are:\n{'\n'.join(items)}" 
    # Read agent config for modelId
    agent_json = os.path.join(work_dir, ".agent", "agent.json")
    try:
        with open(agent_json, "r") as f:
            config = json.load(f)
        model_id = config.get("modelId")
    except Exception as e:
        return f"Failed reading agent config {agent_json}: {e}"
    if not model_id:
        return "modelId not found in agent.json"

    # Call codex CLI
    try:
        env = os.environ.copy()
        # Ensure non-interactive mode
        env["CI"] = "true"
        env["TERM"] = "dumb"
        env["NO_COLOR"] = "1"
        env["FORCE_COLOR"] = "0"
        
        # Use subprocess.run with explicit stream handling
        result = subprocess.run(
            ["codex", "--quiet", "--model", model_id], 
            input=request,
            cwd=work_dir, 
            text=True, 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        return f"Codex CLI failed: {e}\nStderr: {e.stderr if hasattr(e, 'stderr') else 'No stderr available'}"
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
