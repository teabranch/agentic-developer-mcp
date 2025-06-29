"""
FastMCP Agentic Developer MCP Server
"""

from fastmcp import FastMCP
import subprocess
import tempfile
import os
import json
import pwd
import grp

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
def clone_and_write_prompt(repository: str, request: str, componentName: str = "/") -> str:
    """When you need to shallow clone a Git repository, optionally limiting to a specific componentName's folder and its descendants, then read its system prompt and agent config and run Codex CLI accordingly."""
    #componentName is most right part of componentName
    temp_dir = tempfile.mkdtemp() + componentName.lstrip('/')
    try:        
        # Clean up any existing directory
        if os.path.exists(temp_dir):
            subprocess.check_call(["rm", "-rf", temp_dir])
            
        # Clone the repository
        # if folder not in ('', '/'):
        #     # Use sparse-checkout for specific folder
        #     subprocess.check_call(["git", "clone", "--filter=blob:none", "--sparse", repository, temp_dir])
        #     subprocess.check_call(["git", "-C", temp_dir, "sparse-checkout", "set", folder.lstrip('/')])
        # else:
        # Full clone for root folder
        subprocess.check_call(["git", "clone", repository, temp_dir])
    except subprocess.CalledProcessError as e:
        return f"Failed to clone {repository}: {e}"
    # Determine working directory inside clone
    #work_dir = temp_dir if folder in ('', '/') else os.path.join(temp_dir, folder.lstrip('/'))
    work_dir = temp_dir  # Use the root of the cloned repository
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
        
        # Get the Git SSH key from environment
        git_pat_key = os.environ.get("GIT_PAT_KEY", "")
        git_username = os.environ.get("GIT_USERNAME", "")
        # If not found in environment, try to read from common locations
        if not openai_api_key or not git_pat_key or not git_username:
            # Try reading from .env file in project root
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY=') and not openai_api_key:
                            openai_api_key = line.split('=', 1)[1].strip().strip('"\'')
                        elif line.startswith('GIT_PAT_KEY=') and not git_pat_key:
                            git_pat_key = line.split('=', 1)[1].strip().strip('"\'')
                        elif line.startswith('GIT_USERNAME=') and not git_username:
                            git_username = line.split('=', 1)[1].strip().strip('"\'')
                        if openai_api_key and git_pat_key and git_username:
                            break
        
        print(f"About to run codex CLI with model {model_id} in {work_dir} and request {request} using OpenAI API key: {len(openai_api_key)} chars")
        
        # Validate OpenAI API key
        if not openai_api_key:
            return "OPENAI_API_KEY environment variable is not set. Please ensure it's exported in your shell or add it to the MCP server config 'env' section. Current env vars: " + str(list(os.environ.keys()))
        
        # Build Docker command - keep --tty since codex needs it
        # Add --user flag to run container with host user's UID:GID to avoid permission issues
        # Works: docker run --rm --tty -v /tmp/tmp342f6goc:/workspace -e OPENAI_API_KEY=${OPENAI_API_KEY} -e VOLUME_PATH=/workspace codex-cli -a full-auto --model gpt-4o "Write hello world app"
        
        # Get current user's UID and GID to avoid permission issues
        import pwd
        import grp
        current_uid = os.getuid()
        current_gid = os.getgid()
        
        docker_cmd = [
            "docker", "run", "--rm", "--tty",
            "-v", f"{work_dir}:/workspace",
            "-e", f"OPENAI_API_KEY={openai_api_key}",
            "-e", "VOLUME_PATH=/workspace",
            "codex-cli",
            "-a", "full-auto", "--model", model_id, "system: " + system_prompt + ";; user: " + request
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
        # Fix permissions on all files in the work directory after Docker execution
        # Use sudo if available as fallback for permission issues
        try:
            print(f"Fixing permissions on files in {work_dir}")
            
            # First try with regular chmod
            chmod_result = subprocess.run([
                "chmod", "-R", "755", work_dir
            ], capture_output=True, text=True)
            
            if chmod_result.returncode != 0:
                print(f"Regular chmod failed: {chmod_result.stderr}")
                # Try with sudo as fallback
                sudo_result = subprocess.run([
                    "sudo", "chmod", "-R", "755", work_dir
                ], capture_output=True, text=True)
                
                if sudo_result.returncode != 0:
                    print(f"Sudo chmod also failed: {sudo_result.stderr}")
                    # Try to fix ownership first, then permissions
                    subprocess.run([
                        "sudo", "chown", "-R", f"{current_uid}:{current_gid}", work_dir
                    ], capture_output=True, text=True)
                    
                    subprocess.run([
                        "chmod", "-R", "755", work_dir
                    ], capture_output=True, text=True)
                    
            print("Permissions fixed successfully")
        except subprocess.CalledProcessError as perm_error:
            print(f"Warning: Failed to fix permissions: {perm_error}")
            output += f"\n\nWarning: Failed to fix file permissions: {perm_error}"
        except Exception as perm_exception:
            print(f"Warning: Unexpected error fixing permissions: {perm_exception}")
            output += f"\n\nWarning: Unexpected error fixing permissions: {perm_exception}"
        
        # Create branch with unix timestamp, commit all changes and push
        try:
            import time
            unix_timestamp = int(time.time())
            branch_name = f"automated_{componentName}_{unix_timestamp}"
            
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
                print(f"Git add failed, trying to fix permissions and retry...")
                # Try to fix any remaining permission issues before git operations
                try:
                    subprocess.run([
                        "sudo", "chown", "-R", f"{current_uid}:{current_gid}", work_dir
                    ], capture_output=True, text=True, check=False)
                    
                    # Retry git add
                    add_retry = subprocess.run(
                        ["git", "-C", work_dir, "add", "."],
                        capture_output=True,
                        text=True
                    )
                    
                    if add_retry.returncode != 0:
                        output += f"\n\nWarning: Failed to add files to git even after permission fix. Return code: {add_retry.returncode}"
                        output += f"\nStdout: {add_retry.stdout}"
                        output += f"\nStderr: {add_retry.stderr}"
                        output += f"\nWorking directory: {work_dir}"
                        output += f"\nDirectory contents: {os.listdir(work_dir) if os.path.exists(work_dir) else 'N/A'}"
                        return output
                except Exception as fix_error:
                    output += f"\n\nWarning: Failed to add files to git. Return code: {add_result.returncode}"
                    output += f"\nStdout: {add_result.stdout}"
                    output += f"\nStderr: {add_result.stderr}"
                    output += f"\nPermission fix error: {fix_error}"
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
                
                # Setup PAT authentication if GIT_PAT_KEY is available
                if git_pat_key:
                    try:                      
                        # Parse the repository URL to extract components
                        # repository format: https://github.com/owner/repo.git
                        if repository.startswith('https://'):
                            # Extract host and path from repository URL
                            url_parts = repository.replace('https://', '').split('/', 1)
                            git_host = url_parts[0]
                            repo_path = url_parts[1]
                            
                            # Create authenticated URL
                            auth_url = f"https://{git_username}:{git_pat_key}@{git_host}/{repo_path}"
                            
                            # Set the remote URL with PAT authentication
                            subprocess.check_call([
                                "git", "-C", work_dir, "remote", "set-url", "origin", auth_url
                            ])
                            
                            print(f"Set remote URL with PAT authentication for user: {git_username}")
                        
                        # Push the new branch
                        subprocess.check_call([
                            "git", "-C", work_dir, "push", "-u", "origin", branch_name
                        ])
                        
                        output += f"\n\nChanges saved to branch: {branch_name} (using PAT authentication)"
                        
                    except subprocess.CalledProcessError as auth_error:
                        output += f"\n\nWarning: Failed to set up PAT authentication username: {git_username} pat: {len(git_pat_key)}: {auth_error}"
                        # Fallback to regular push
                else:
                    # Fallback to regular push (will likely fail without proper auth)
                    subprocess.check_call([
                        "git", "-C", work_dir, "push", "-u", "origin", branch_name
                    ])
                    
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
