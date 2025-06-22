FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for Codex CLI and uv
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Codex CLI globally
RUN npm install -g @openai/codex

# Copy Python requirements and install
# Copy src and all folders and files in it
COPY src ./src/
RUN cd src && uv pip install --system -e .

# Copy application code
COPY . .

# Expose port for MCP server with running port from 8080 to 8180
ARG MCP_PORT=8180
ENV MCP_PORT=${MCP_PORT}
EXPOSE ${MCP_PORT}

# Start the Python MCP server using uv with SSE transport on the specified port
CMD ["/bin/bash", "-c", "uv run python -m mcp_server.server --transport sse --host 0.0.0.0 --port ${MCP_PORT}"]
