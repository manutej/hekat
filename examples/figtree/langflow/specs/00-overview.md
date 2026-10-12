# How Langflow agent workflows coordinate

A chat message reaches an Agent, which calls tools, reads stored messages and answers, while flows are also served to outside programs through the Workflow API and an MCP server. Read it first to see which actors the nine workflow specs share.

## Components
- **Chat Input** (kind: terminal, icon: user): where the user's message enters the flow.
- **Agent** (kind: block, icon: gear): the primary agent actor; decides when to call tools and answers.
- **Tool** (kind: block, icon: wrench): a component in Tool Mode, or a second Agent, that the Agent calls.
- **MCP Server** (kind: block, icon: ports): hosts tools for agents, and lists a project's flows as tools for MCP clients.
- **Langflow Storage** (kind: store, icon: database): the database where chat messages are saved by session ID.
- **Flow** (kind: block, icon: layers): a flow that Langflow runs, serves as an MCP tool, or executes by flow ID.
- **Workflow API** (kind: block, icon: render): the endpoint that runs a flow for an outside program.
- **External Application** (kind: actor, icon: document): the app, script or website that calls Langflow from outside.
- **Chat Output** (kind: terminal, icon: text): returns the agent's response.

## Flows
Chat Input → Agent → Chat Output
Agent → Tool (control): the agent calls a tool through its Tools port.
Tool → MCP Server (control): Langflow runs the command to launch the server when a tool is needed.
Langflow Storage → Agent (data): the built-in chat memory reads stored messages for the session.
Flow → MCP Server (data): each enabled flow is registered as a tool on the server.
External Application → Workflow API (control): the application sends a request with the flow ID.
Workflow API → Flow (control): the API executes the flow in the selected mode.

## Steps
1. Start with agent-with-tools to see the Agent call Tool components from Chat Input to Chat Output.
2. Read agent-as-tool to see a second Agent attached as a Tool.
3. Read mcp-client to see the Agent reach tools hosted on an MCP Server.
4. Read mcp-server to see a Flow served as a tool on the MCP Server.
5. Read memory-and-sessions to see the Agent read Langflow Storage by session ID.
6. Read loops-and-routing to see branching, looping and sub-flows inside a Flow.
7. Read human-in-the-loop to see a Flow pause for a human decision.
8. Read run-flow-api to see an External Application run a Flow through the Workflow API.
9. Read a2a-agents to see Flows called as agents by other agents and clients.

## Not in the documentation
- The pages do not say that MCP clients or A2A clients use the Workflow API; each has its own endpoint, so they are not drawn here.
- The pages do not draw the Agent writing to Langflow Storage as a separate arrow; the Chat Output is stored by a second Message History component.
- The pages do not state which Flow contains the Agent in the tool and memory specs.

```evidence
Chat Input: "such as a **Chat Input** component" (Agents_agents.mdx)
Agent: "The **Agent** component is the primary agent actor in your agent flows." (Components_components-agents.mdx)
Tool: "the agent decides when to call on certain tools" (Agents_agents-tools.mdx)
MCP Server: "MCP servers host tools that agents (MCP clients) use to complete specialized tasks." (Tutorials_mcp-tutorial.mdx)
Langflow Storage: "Messages are stored in the database with session IDs as a reference." (Develop_session-id.mdx)
Flow: "Langflow automatically adds the project to your MCP server's configuration and makes the project's flows available as MCP tools." (Agents_mcp-server.mdx)
Workflow API: "The Workflow API provides programmatic access to execute Langflow workflows" (API-Reference_workflows-api.mdx)
External Application: "Langflow provides several ways to run flows from external applications:" (Flows_concepts-publish.mdx)
Chat Output: "which is typically connected to a **Chat Output** component." (Agents_agents.mdx)
Agent → Tool: "Connect the **Toolset** port for each tool component to the **Tools** port on the **Agent** component." (Agents_agents.mdx)
Tool → MCP Server: "Langflow runs the command to launch the server when the agent determines that it needs to use a tool provided by that server." (Tutorials_mcp-tutorial.mdx)
Langflow Storage → Agent: "**Agent component**: This component has built-in chat memory that is enabled by default." (Develop_memory.mdx)
Flow → MCP Server: "Once your MCP client is connected to your Langflow project's MCP server, your flows are registered as tools." (Agents_mcp-server.mdx)
External Application → Workflow API: "executes Langflow flows over `POST /api/v2/workflows` in three modes" (API-Reference_workflow-api-quickstart.mdx)
Workflow API → Flow: "Execute a workflow in `sync`, `stream`, or `background` mode." (API-Reference_workflows-api.mdx)
```
