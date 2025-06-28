#!/bin/bash
# Build the codex Docker image
docker build -f Dockerfile.codex -t codex-cli .

pip3 install open-responses-server

otc start