#!/bin/bash
set -e

echo "Building and starting Codex MCP wrapper with open-responses-server..."
docker-compose up --build

# If you want to run in detached mode, use:
# docker-compose up -d --build