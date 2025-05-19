#!/bin/bash
set -e

echo "Building and starting Codex MCP wrapper, Codex CLI, and open-responses-server via Docker Compose..."
docker-compose up --build
