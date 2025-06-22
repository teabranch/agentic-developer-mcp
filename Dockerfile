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
COPY src/pyproject.toml ./src/
COPY src/README.md ./src/
RUN cd src && uv pip install --system -e .

# Copy application code
COPY . .

# Expose port for MCP server
EXPOSE 8080

# Start the Python MCP server using uv
CMD ["uv", "run", "--system", "python", "-m", "src.mcp_server.server"]
