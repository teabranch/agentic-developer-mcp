"""
MCP Server Implementation for Agentic Developer

This server opens a Git repository and runs Codex on its contents.
"""

import os
import click
import anyio
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool

# Create server
mcp = FastMCP("Agentic Developer MCP Server")

class RepositoryConfig(BaseModel):
    """Configuration for the Git repository"""
    repository: str = Field(description="Git repository URL")
    branch: Optional[str] = Field(default=None, description="Git branch to checkout")
    folder: Optional[str] = Field(default=None, description="Folder within the repository to focus on")
    request: str = Field(description="Codex request/prompt to run")

@mcp.tool()
async def run_codex(config: RepositoryConfig) -> str:
    """
    Clone a repository, checkout a specific branch (optional), 
    navigate to a specific folder (optional), and run Codex with the given request.
    
    Args:
        config: Repository configuration including repository URL, branch, folder and request
        
    Returns:
        Result from Codex execution
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Clone the repository
        clone_cmd = ["git", "clone", config.repository, str(temp_path)]
        process = await anyio.to_thread.run_sync(
            lambda: subprocess.run(clone_cmd, capture_output=True, text=True)
        )
        
        if process.returncode != 0:
            return f"Error cloning repository: {process.stderr}"
        
        # Checkout the branch if specified
        if config.branch:
            checkout_cmd = ["git", "-C", str(temp_path), "checkout", config.branch]
            process = await anyio.to_thread.run_sync(
                lambda: subprocess.run(checkout_cmd, capture_output=True, text=True)
            )
            
            if process.returncode != 0:
                return f"Error checking out branch {config.branch}: {process.stderr}"
        
        # Determine the work directory
        work_dir = temp_path
        if config.folder:
            work_dir = work_dir / config.folder
            if not work_dir.exists():
                return f"Error: Folder {config.folder} does not exist in the repository"
        
        # Run Codex with the given request
        # This is a placeholder for the actual Codex execution
        # In a real implementation, you would invoke the Codex API here
        return run_mock_codex(str(work_dir), config.request)

def run_mock_codex(folder_path: str, request: str) -> str:
    """
    Mock implementation of running Codex
    In a real implementation, this would call the Codex API
    
    Args:
        folder_path: Path to the folder to run Codex on
        request: Codex request/prompt
        
    Returns:
        Result from Codex execution
    """
    # List files in the directory to simulate analysis
    files = list(Path(folder_path).glob('**/*'))
    file_list = "\n".join([f"- {file.relative_to(folder_path)}" for file in files if file.is_file()])
    
    return f"""
Codex execution completed successfully.
Working directory: {folder_path}
Request: {request}

Files analyzed:
{file_list}

Mock response: This is a placeholder for the actual Codex response.
In a real implementation, Codex would analyze the repository and generate a response based on the request.
"""

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)"
)
def main(port: int, transport: str) -> int:
    """Run the MCP server"""
    if transport == "sse":
        from mcp.server.sse import run_sse_server
        import uvicorn
        
        app = run_sse_server(mcp.app, "/messages/")
        uvicorn.run(app, host="127.0.0.1", port=port)
    else:
        from mcp.server.stdio import run_stdio_server
        run_stdio_server(mcp.app)
    
    return 0

if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
