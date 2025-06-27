#!/bin/bash

# Script to start multiple instances of the MCP server with different ports
# Each instance gets its own container names and port assignments
# Set SINGLE_INSTANCE=1 environment variable to start only one instance

set -e

# Check if single instance mode is requested
if [ "${SINGLE_INSTANCE:-0}" = "1" ]; then
    echo "Single instance mode requested. Starting one instance..."
    exec ./start-single.sh
fi

# Default configuration
DEFAULT_INSTANCES=3
DEFAULT_BASE_MCP_PORT=8180
DEFAULT_BASE_RESPONSES_PORT=3000

# Parse command line arguments
INSTANCES=${1:-$DEFAULT_INSTANCES}
BASE_MCP_PORT=${2:-$DEFAULT_BASE_MCP_PORT}
BASE_RESPONSES_PORT=${3:-$DEFAULT_BASE_RESPONSES_PORT}

# Validate inputs
if ! [[ "$INSTANCES" =~ ^[0-9]+$ ]] || [ "$INSTANCES" -lt 1 ] || [ "$INSTANCES" -gt 10 ]; then
    echo "Error: Number of instances must be between 1 and 10"
    exit 1
fi

echo "Starting $INSTANCES instances of the MCP server..."
echo "Base MCP port: $BASE_MCP_PORT"
echo "Base Responses port: $BASE_RESPONSES_PORT"
echo

# Function to check if port is available
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        return 1  # Port is in use
    fi
    return 0  # Port is available
}

# Function to find next available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    while ! check_port $port; do
        ((port++))
        if [ $port -gt $((start_port + 100)) ]; then
            echo "Error: Could not find available port starting from $start_port"
            exit 1
        fi
    done
    echo $port
}

# Array to store instance information
declare -a INSTANCE_INFO

# Start each instance
for i in $(seq 1 $INSTANCES); do
    echo "Starting instance $i..."
    
    # Calculate ports for this instance
    MCP_PORT=$(find_available_port $((BASE_MCP_PORT + i - 1)))
    RESPONSES_PORT=$(find_available_port $((BASE_RESPONSES_PORT + i - 1)))
    
    # Export environment variables for docker-compose
    export INSTANCE_ID=$i
    export MCP_PORT=$MCP_PORT
    export MCP_HOST_PORT=$MCP_PORT
    export RESPONSES_HOST_PORT=$RESPONSES_PORT
    
    echo "  Instance $i:"
    echo "    MCP Server: http://localhost:$MCP_PORT"
    echo "    Responses Server: http://localhost:$RESPONSES_PORT"
    
    # Start the instance in detached mode
    docker-compose up -d --build
    
    # Store instance information
    INSTANCE_INFO[$i]="Instance $i: MCP=http://localhost:$MCP_PORT, Responses=http://localhost:$RESPONSES_PORT"
    
    # Wait a bit between starts to avoid conflicts
    sleep 2
done

echo
echo "All instances started successfully!"
echo
echo "Instance Summary:"
for info in "${INSTANCE_INFO[@]}"; do
    echo "  $info"
done

echo
echo "To stop all instances, run: docker-compose down --remove-orphans"
echo "To view logs for a specific instance, run: docker logs codex-mcp-wrapper-<instance_id>"
echo "To view all running containers: docker ps"
