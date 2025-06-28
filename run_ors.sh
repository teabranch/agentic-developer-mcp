#!/bin/bash
# Build the codex Docker image
docker build -f Dockerfile.codex -t codex-cli .

pip3 install open-responses-server

# Export OPENAI_API_KEY to make it available to child processes
export OPENAI_API_KEY="${OPENAI_API_KEY}"

otc start