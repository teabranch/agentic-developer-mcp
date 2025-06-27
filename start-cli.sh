#!/bin/bash

# Script to start a single instance of the MCP server
# This is a simplified version that starts just one pair of services

set -e

echo "Starting single instance of the MCP server..."
echo "MCP Server will be available at: http://localhost:8180"
echo "Responses Server will be available at: http://localhost:3000"
echo

# Start the single instance
docker-compose -f docker-compose.cli.yml up -d --build

echo
echo "Single instance started successfully!"
echo
echo "Services:"
echo "  MCP Server: http://localhost:8180"
echo "  Responses Server: http://localhost:3000"
echo
echo "MCP Configuration:"
echo "  Use servers_config.json for MCP client integration"
echo "  Server URL: http://localhost:8180"
echo
echo "To stop the instance, run: docker-compose -f docker-compose.1.yml down"
echo "To view logs, run: docker-compose -f docker-compose.1.yml logs -f"
echo "To view running containers: docker ps"
