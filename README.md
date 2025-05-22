# Agentic Developer Mcp

## Table of contents

- Introduction 
- Step 1 - Codex: "Cursor on a pipeline" 
- Step 2 - Prepare "workbenches" 
- Step 3 - Connect recursively 

## Introduction

### What is the Workbench Development paradigm?

Workbench Development is a new paradigm, which puts the developer as a leader of a fleet of AI Agents to write code, but in a structured manner that gives them full control over the outcomes. 

### What is Agentic Developer MCP?

Agentic Developer MCP is a server built on OpenAI's Codex, and connects it to an AI client like Cursor via MCP, and connects recursively to itself via MCPs.  

It is built on OpenAI's Responses API, and works with local and hosted models to give developers full control and privacy over their models and code.  

AgenticBench allows tailoring environments for each agent to create their components with the highest, repeatable accuracy. 

## Design

### Step 1 - Codex: "Cursor on a pipeline" 

- Codex is an AI code writer CLI by OpenAI that operates AI. 
- [Open Responses Server (ORS)](https://github.com/TeaBranch/open-responses-server) is an open-source layer written by TeaBranch team (Ori Nachum, Danny Teller, and Allen Jacobson) that connects your AI provider with Codex. 
- ORS adds MCPs integration. 

 **In plan:** 

- [x] Add MCP support (Implement MCP client)   
- [ ] Add MCP server support (Wrap as MCP server) 
- [ ] Add Web Search MCP 
- [ ] Add Files search MCP 
- [ ] Add Code Interpreter MCP 


### Step 2 - Prepare "workbenches"

Workbenches are predefined folders with basic projects.  
Each has the most empty, unchanging structure, which would give Codex an environment in which we create similar components. (Web app components, C# service classes, etc.).  
Since the environment never changes, the prompts can be static and give the same results.  

Each component is tested in this sterile environment and committed to a branch.

### Step 3 - Connect recursively 

Each Codex pipeline is connected to Codex via MCP.  
Components are built “bottom up” and the caller AI Agent works on merging them.  

In case of an issue, the developer can review the prepare components, change them, and continue from where they stopped.

**This paradigm shifts the developer from a direct code handler, to a higher level team lead of AI Agents.**


