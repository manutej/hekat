# An agent calling tools

A Langflow Agent component receives a chat message and answers it, calling connected tool components when it decides they can help. Build it when a chat flow must search the web, fetch pages or calculate rather than rely only on the model.

## Components
- **Chat Input** (kind: terminal, icon: user): where the user's message enters the flow.
- **Agent** (kind: block, icon: gear): the primary agent actor; uses an LLM to respond and decides when to call tools.
- **Web Search** (kind: block, icon: search): a tool component with Tool Mode enabled.
- **URL** (kind: block, icon: document): a tool component with Tool Mode enabled that fetches web content.
- **Calculator** (kind: block, icon: wrench): a tool component with Tool Mode enabled for arithmetic.
- **Chat Output** (kind: terminal, icon: text): returns the agent's response to the Playground.

## Flows
Chat Input → Agent → Chat Output
Agent → Web Search (control): the agent calls the tool through its Tools port.
Agent → URL (control): the agent calls the tool through its Tools port.
Agent → Calculator (control): the agent calls the tool through its Tools port.

## Steps
1. Add an Agent component and select a model from the Language Model dropdown.
2. Add Chat Input and Chat Output components and connect them to the Agent.
3. Add Web Search, URL and Calculator components and enable Tool Mode on each.
4. Connect the Toolset port of each tool to the Tools port on the Agent.
5. Open the Playground and ask a question that needs a tool, such as a news summary.
6. Read the tool calls, their input and the raw output in the Playground.

## Not in the documentation
The pages do not draw the tool results as a separate arrow back to the Agent; they describe the Playground showing the raw output the agent received.

```evidence
Chat Input: "such as a **Chat Input** component" (Agents_agents.mdx)
Agent: "The **Agent** component is the primary agent actor in your agent flows." (Components_components-agents.mdx)
Web Search: "Add **Web Search**, **URL**, and **Calculator** components to your flow." (Agents_agents.mdx)
URL: "Enable **Tool Mode** in the **Web Search**, **URL**, and **Calculator** components:" (Agents_agents.mdx)
Calculator: "Repeat for the **URL** and **Calculator** components." (Agents_agents.mdx)
Chat Output: "which is typically connected to a **Chat Output** component." (Agents_agents.mdx)
Agent → Web Search: "Connect the **Toolset** port for each tool component to the **Tools** port on the **Agent** component." (Agents_agents.mdx)
Agent → URL: "the agent decides when to call on certain tools" (Agents_agents-tools.mdx)
Agent → Calculator: "a component can accept requests from an **Agent** component to use the component's available actions as tools" (Agents_agents.mdx)
```
