# An agent using an MCP server's tools

The MCP Tools component connects an external MCP server to a Langflow Agent so the agent can use the server's tools when answering a prompt. Build it when the agent needs specialized tools such as weather or fetch.

## Components
- **Chat Input** (kind: terminal, icon: user): receives the prompt from a user or application and triggers the flow.
- **Agent** (kind: block, icon: gear): decides whether a connected tool can help and calls it.
- **MCP Tools** (kind: block, icon: wrench): connects to one registered MCP server and exposes its tools through the Toolset port in Tool Mode.
- **MCP Server** (kind: store, icon: database): the external server, registered in Settings, that hosts the tools.
- **Chat Output** (kind: terminal, icon: document): returns the final response to the user or application.

## Flows
Chat Input → Agent → Chat Output
Agent → MCP Tools (control): the agent calls the tool through the Tools port when it decides the server can help.
MCP Tools → MCP Server (control): Langflow launches or calls the server to run the selected tool.

## Steps
1. Register the MCP server in Settings or the MCP sidebar with JSON, STDIO, or HTTP/SSE.
2. Add the MCP Tools component and select the registered server in the MCP Server field.
3. Select a tool, or leave it blank to allow all tools.
4. Enable Tool Mode on MCP Tools and connect its Toolset port to the Tools port of the Agent.
5. Attach Chat Input and Chat Output to the Agent.
6. Open the Playground and ask a question that needs the tool.

## Not in the documentation
The pages do not state how the Agent and the MCP server exchange messages on the wire.

```evidence
Chat Input: "The **Chat Input** component is connected to the **Agent** component's **Input** port." (Tutorials_mcp-tutorial.mdx)
Agent: "an **Agent** component in a Langflow flow can use connected components as tools to handle requests." (Tutorials_mcp-tutorial.mdx)
MCP Tools: "The **MCP Tools** component connects to a Model Context Protocol (MCP) server and exposes the MCP server's functions as tools for Langflow agents to use to respond to input." (Components_mcp-tools.mdx)
MCP Server: "MCP servers host tools that agents (MCP clients) use to complete specialized tasks." (Tutorials_mcp-tutorial.mdx)
Chat Output: "which returns the final response to the user or application." (Tutorials_mcp-tutorial.mdx)
Agent → MCP Tools: "The agent calls the MCP server function `fetch`, and then returns the response." (Agents_mcp-client.mdx)
MCP Tools → MCP Server: "Langflow runs the command to launch the server when the agent determines that it needs to use a tool provided by that server." (Tutorials_mcp-tutorial.mdx)
```
