# Flows exposed as tools to MCP clients

A Langflow project has its own MCP server that exposes the project's flows as tools. MCP clients such as Cursor connect to that server and call the tools when generating responses.

## Components
- **Langflow Project** (kind: store, icon: layers): the container whose flows are served; each project has its own MCP server.
- **Flow** (kind: block, icon: gear): a flow in the project that is served as one MCP tool, with a tool name and description.
- **Chat Output** (kind: terminal, icon: document): the component a flow must contain to be used as an MCP tool.
- **MCP Server** (kind: block, icon: ports): the project's server that lists the enabled flows as tools over streamable HTTP or SSE.
- **MCP Client** (kind: actor, icon: user): a client such as Cursor that connects to the server and calls the tools.
- **MCP Inspector** (kind: actor, icon: eye): a tool for testing and debugging the server and its registered tools.

## Flows
Langflow Project → MCP Server (data): the project is added to the server configuration and its flows become tools.
Flow → Chat Output (data): the flow ends in a Chat Output component.
Flow → MCP Server (data): each enabled flow is registered as a tool on the server.
MCP Client → MCP Server (control): the client decides when to use a flow tool and calls it.
MCP Inspector → MCP Server (control): the inspector connects to the server to list and test the tools.

## Steps
1. Create a Langflow project with at least one flow that has a Chat Output component.
2. Select which flows are exposed as tools on the MCP Server tab.
3. Edit each tool name and description so clients can pick the right tool.
4. Set the authentication method for the project's MCP server.
5. Add the server to an MCP client with the JSON snippet or Auto install.
6. Test the tools in MCP Inspector, then ask the client a question that needs a flow.

## Not in the documentation
The pages do not state how the MCP Server runs a flow internally after a tool call arrives.
The pages do not draw a direct link between the coding agents of the Langflow MCP Client setting and the project MCP server.

```evidence
Langflow Project: "Each [Langflow project](/concepts-flows#projects) has its own MCP server with its own MCP server authentication settings." (Agents_mcp-server.mdx)
Flow: "Langflow automatically adds the project to your MCP server's configuration and makes the project's flows available as MCP tools." (Agents_mcp-server.mdx)
Chat Output: "The **Chat Output** component is required to use a flow as an MCP tool." (Agents_mcp-server.mdx)
MCP Server: "Langflow MCP servers support both the **streamable HTTP** transport and **Server-Sent Events (SSE)** as a fallback." (Agents_mcp-server.mdx)
MCP Client: "Cursor determines when to use tools based on your queries, and requests permissions when necessary." (Agents_mcp-server.mdx)
MCP Inspector: "[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is a common tool for testing and debugging MCP servers." (Agents_mcp-server.mdx)
MCP Client → MCP Server: "Once your MCP client is connected to your Langflow project's MCP server, your flows are registered as tools." (Agents_mcp-server.mdx)
MCP Inspector → MCP Server: "In the MCP Inspector UI, enter the connection details for your Langflow project's MCP server." (Agents_mcp-server.mdx)
```
