FROM node:20-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package.json ./
RUN npm install

# Install Codex CLI globally
RUN npm install -g @openai/codex

# Copy application code
COPY . .

# Expose port for MCP server
EXPOSE 8080

# Start the MCP server
CMD ["node", "mcp-server.js"]
