"""
FastMCP Echo Server
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import tempfile
import os

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


@mcp.tool()
def clone_and_write_prompt(repository: str, request: str) -> str:
    """Clone the repository and write the request to a .prompt file."""
    # Create a temporary directory for cloning
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository into the temporary directory
        subprocess.check_call(["git", "clone", repository, temp_dir])
    except subprocess.CalledProcessError as e:
        return f"Failed to clone {repository}: {e}"
    # Write the request to a .prompt file in the cloned repo
    prompt_path = os.path.join(temp_dir, ".prompt")
    with open(prompt_path, "w") as f:
        f.write(request)
    return f"Repository cloned to {temp_dir} and request written to .prompt"
