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
    try:        
        # Clean up any existing directory
        if os.path.exists(temp_dir):
            subprocess.check_call(["rm", "-rf", temp_dir])
            
        # Clone the repository
        if folder not in ('', '/'):
            # Use sparse-checkout for specific folder
            subprocess.check_call(["git", "clone", "--filter=blob:none", "--sparse", repository, temp_dir])
            subprocess.check_call(["git", "-C", temp_dir, "sparse-checkout", "set", folder.lstrip('/')])
        else:
            # Full clone for root folder
            subprocess.check_call(["git", "clone", repository, temp_dir])
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

    # Call codex CLI via Docker
    try:
        # Get the OpenAI API key from environment
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # If not found in environment, try to read from common locations
        if not openai_api_key:
            # Try reading from .env file in project root
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY='):
                            openai_api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
        
        print(f"About to run codex CLI with model {model_id} in {work_dir} and request {request} using OpenAI API key: {len(openai_api_key)} chars")
        
        # Validate OpenAI API key
        if not openai_api_key:
            return "OPENAI_API_KEY environment variable is not set. Please ensure it's exported in your shell or add it to the MCP server config 'env' section. Current env vars: " + str(list(os.environ.keys()))
        
        # Build Docker command - keep --tty since codex needs it
        # Works: docker run --rm --tty -v /tmp/tmp342f6goc:/workspace -e OPENAI_API_KEY=${OPENAI_API_KEY} -e VOLUME_PATH=/workspace codex-cli -a full-auto --model gpt-4o "Write hello world app"
        docker_cmd = [
            "docker", "run", "--rm", "--tty",
            "-v", f"{work_dir}:/workspace",
            "-e", f"OPENAI_API_KEY={openai_api_key}",
            "-e", "VOLUME_PATH=/workspace",
            "codex-cli",
            "-a", "full-auto", "--model", model_id, request
        ]
        
        print(f"Running Docker command: {' '.join(docker_cmd)}")
        print(f"Working directory exists: {os.path.exists(work_dir)}")
        print(f"Working directory contents: {os.listdir(work_dir) if os.path.exists(work_dir) else 'N/A'}")
        
        # Use subprocess.run with Docker to run codex with timeout
        result = subprocess.run(
            docker_cmd,
            text=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,  # 10 minute timeout for codex operations
            check=False  # Don't raise exception, handle manually
        )
        
        print(f"Docker command completed with return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)} chars")
        print(f"Stderr length: {len(result.stderr)} chars")
        
        if result.returncode != 0:
            return f"Codex CLI failed with return code {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"
            
        output = result.stdout
        
        # Create branch with unix timestamp, commit all changes and push
        try:
            import time
            unix_timestamp = int(time.time())
            branch_name = f"automated_{unix_timestamp}"
            
            # Check git status first
            git_check = subprocess.run(
                ["git", "-C", work_dir, "status"],
                capture_output=True,
                text=True
            )
            print(f"Git status check: return code {git_check.returncode}")
            print(f"Git status stdout: {git_check.stdout}")
            print(f"Git status stderr: {git_check.stderr}")
            
            if git_check.returncode != 0:
                output += f"\n\nWarning: Git repository not properly initialized or accessible. Status check failed: {git_check.stderr}"
                return output
            
            # Create and checkout new branch
            subprocess.check_call(["git", "-C", work_dir, "checkout", "-b", branch_name])
            
            # Add all changes with better error handling
            add_result = subprocess.run(
                ["git", "-C", work_dir, "add", "."],
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                output += f"\n\nWarning: Failed to add files to git. Return code: {add_result.returncode}"
                output += f"\nStdout: {add_result.stdout}"
                output += f"\nStderr: {add_result.stderr}"
                output += f"\nWorking directory: {work_dir}"
                output += f"\nDirectory contents: {os.listdir(work_dir) if os.path.exists(work_dir) else 'N/A'}"
                return output
            
            # Check if there are any changes to commit
            git_status = subprocess.run(
                ["git", "-C", work_dir, "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if git_status.stdout.strip():  # There are changes to commit
                # Commit changes
                subprocess.check_call([
                    "git", "-C", work_dir, "commit", 
                    "-m", f"Automated changes from Codex CLI - {branch_name} request: {request}"
                ])
                
                # # Push the new branch
                # subprocess.check_call([
                #     "git", "-C", work_dir, "push", "origin", branch_name
                # ])
                
                output += f"\n\nChanges saved to branch: {branch_name}"
            else:
                output += f"\n\nNo changes to commit. Branch {branch_name} created but not pushed."
                
        except subprocess.CalledProcessError as git_error:
            output += f"\n\nWarning: Failed to save changes to git: {git_error}"
        except Exception as git_exception:
            output += f"\n\nWarning: Unexpected error during git operations: {git_exception}"
            
    except subprocess.TimeoutExpired as e:
        return f"Codex CLI timed out after 10 minutes: {e}"
    except subprocess.CalledProcessError as e:
        return f"Codex CLI failed: {e}\nStderr: {e.stderr if hasattr(e, 'stderr') else 'No stderr available'}"
    except Exception as e:
        return f"Unexpected error running Codex CLI: {e}"
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
