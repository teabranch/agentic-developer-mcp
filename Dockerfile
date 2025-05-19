FROM node:20

# Install Codex CLI	run npm install -g @openai/codex

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .

EXPOSE 8080
CMD ["node", "mcp-server.js"]
