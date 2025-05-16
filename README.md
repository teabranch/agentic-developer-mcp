# Agentic Workbench Mcp

## Table of contents

- [cite_start] What is WorkbenchMCP? 
- [cite_start] Step 1 - Codex: "Cursor on a pipeline" 
- [cite_start] Step 2 - Prepare "workbenches" 
- [cite_start] Step 3 Connect recursively 

## What is the Workbench Development paradigm?

[cite_start] Workbench Development is a new paradigm, which puts the developer as a leader of a fleet of AI Agents to write code, but in a structured manner that gives them full control over the outcomes. 

## What is WorkbenchMCP?

[cite_start] WorkbenchMCP is a tool that built on OpenAI's Codex, and connects it to an AI client like Cursor via MCP, and connects recursively to itself via MCPs. 
[cite_start] It is built on OpenAI's Responses API, and works with local and hosted models to give developers full control and privacy over their models and code. 
[cite_start] WorkbenchMCP allows tailoring environments for each agent to create their components with the highest, repeatable accuracy. 

## Design

### [cite_start] Step 1 - Codex: "Cursor on a pipeline" 

[cite_start] Codex is an AI code writer CLI by OpenAI that operates AI. 
[cite_start] [Open Responses Server (ORS)](https://github.com/TeaBranch/open-responses-server) is an open-source layer written by TeaBranch team (Ori Nachum, Danny Teller, and Allen Jacobson) that connects your AI provider with Codex. 
[cite_start] ORS adds MCPs integration. 

[cite_start] **In plan:** 

- [x] Add MCP support (Implement MCP client)   
- [cite_start] Add MCP server support (Wrap as MCP server) 
- [cite_start] Add Web Search MCP 
- [cite_start] Add Files search MCP 
- [cite_start] Add Code Interpreter MCP 
- [cite_start] Add Computer Use MCP 

