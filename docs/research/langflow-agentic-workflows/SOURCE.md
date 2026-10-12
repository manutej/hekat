# Agentic workflows in Langflow

Grounded summary for FigTree teaching figures. See BIBLIOGRAPHY.md for URLs.

## Langflow flow topology

A Langflow **flow** is a canvas of **components** wired by ports. A minimal chat agent flow connects user I/O to the Agent component and the Language Model.

Flow wiring (data path):

Chat Input -> Agent Component
Agent Component -> Chat Output
Language Model -> Agent Component

The Agent Component uses the Language Model as a reasoning engine. The Agent Component selects tools and returns a Response output.

Deep-dive figures: [module 01 flow topology](modules/01-flow-topology/README.md), [module 02 single-agent tool loop](modules/02-single-agent-tool-loop/README.md).

## Single-agent tool loop

Agents extend LLMs by **tool registration**: tools are functions wrapped as Tool objects with descriptions the Agent Component reads at initialization.

Tool attachment workflow:

1. Enable Tool Mode on a tool component
2. Connect Toolset port to Agent Component Tools port
3. Send user prompt through Chat Input

Tool loop (control + data):

Chat Input -> Agent Component
Web Search Component -> Agent Component
URL Component -> Agent Component
Calculator Component -> Agent Component
Agent Component -> Chat Output

During a Playground run, Langflow sends events for the input message, each tool call, streaming tokens, and the final answer. When the run finishes, Langflow writes the completed message to chat history.

## Agent memory and session scope

The Agent Component has built-in chat memory enabled by default. Memories group by session_id.

Memory workflow:

Chat Input -> Agent Component
Agent Component -> Storage Backend
Storage Backend -> Agent Component

Use Message History Component when external memory such as Mem0 is required.

## MCP client pattern

Langflow integrates MCP as both MCP server and MCP client. The MCP Tools Component connects an MCP server so the Agent Component can call remote tools.

MCP client wiring:

MCP Server Registry -> MCP Tools Component
MCP Tools Component -> Agent Component
Chat Input -> Agent Component
Agent Component -> Chat Output

Register MCP server workflow:

1. Open Settings MCP Servers and click Add MCP Server
2. Drag the server from MCP sidebar to canvas
3. Enable Tool Mode on MCP Tools Component
4. Connect MCP Tools Component Toolset port to Agent Component Tools port

One MCP Tools Component is required per external MCP server.

## MCP server pattern (flows as tools)

Each Langflow project runs an MCP server that exposes project flows as MCP tools. External MCP clients call those tools over HTTP/SSE.

Flows-as-tools chain:

Langflow Project -> Project MCP Server
Project MCP Server -> External MCP Client

HTTP/SSE endpoint example:

Project MCP Server -> MCP Tools Component

When a nested flow runs as MCP server and contains MCP Tools Component calling an external server, Langflow can propagate x-api-key or Authorization headers to the nested server.

## Multi-tool agent coordination

An Agent Component can use any Langflow component as a tool, including other Agent components and MCP servers.

Multi-server MCP workflow (tutorial pattern):

Weather MCP Tools Component -> Agent Component
IP Geolocation MCP Tools Component -> Agent Component
Chat Input -> Agent Component
Agent Component -> Chat Output

The Agent Component may call ip_geolocation tool first, then weather tool, before generating the final Response.

## API and programmatic execution

Applications invoke flows through Langflow API POST /api/v1/run/FLOW_ID. Tweaks can modify MCP Tools Component environment variables at runtime.

API execution path:

Client Application -> Langflow API
Langflow API -> Agent Flow
Agent Flow -> MCP Tools Component
