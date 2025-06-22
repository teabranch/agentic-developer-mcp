FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for Codex CLI
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Codex CLI globally
RUN npm install -g @openai/codex

# Copy Python requirements and install
COPY src/pyproject.toml ./src/
COPY src/README.md ./src/
RUN pip install -e ./src/

# Copy application code
COPY . .

# Expose port for MCP server
EXPOSE 8080

# Start the Python MCP server
CMD ["python", "-m", "uvicorn", "src.mcp_server.server:mcp.app", "--host", "0.0.0.0", "--port", "8080"]
