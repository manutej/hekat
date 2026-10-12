# A manager agent delegating to other agents

A primary Agent calls a second Agent as a tool, so each specialized agent handles the queries suited to it. Build it when one agent should hand complex or domain-specific work to another model.

## Components
- **Agent** (kind: block, icon: gear): the primary Agent component; decides when to call a tool and answers the user.
- **Agent Tool** (kind: block, icon: gear): a second Agent component set to Tool Mode and attached as a tool (a specialized agent).
- **Tool Mode** (kind: process, icon: wrench): the setting that turns the second Agent into a tool with a Toolset port.
- **Tool Actions** (kind: document, icon: text): the action name, slug and description that tell the primary agent what the tool does.

## Flows
Tool Mode → Agent Tool (data): enabling Tool Mode exposes the Toolset port.
Tool Actions → Agent (data): the action description tells the primary agent what the tool is for.
Agent → Agent Tool (control): the Toolset port of the second agent connects to the Tools port of the primary agent, and the primary agent calls it when needed.

## Steps
1. Create a flow from the starter template.
2. Add a second Agent component and add the API key to both agents.
3. Enable Tool Mode on the second Agent component.
4. Edit the tool's actions so the slug and description say what the agent is for.
5. Connect the second agent's Toolset port to the primary agent's Tools port.

## Not in the documentation
These pages do not name the Chat Input and Chat Output components for this flow, and do not describe how the second agent's answer is passed back to the primary agent.

```evidence
Agent: "attach that agent as a tool for your primary **Agent** component" (Agents_agents-tools.mdx)
Agent Tool: "attach several specialized models to a primary agent, such as agents that are trained on certain tasks or domains" (Agents_agents-tools.mdx)
Tool Mode: "you can set another **Agent** component to **Tool Mode**" (Agents_agents-tools.mdx)
Tool Actions: "Available actions are listed in each tool component's **Actions** list." (Agents_agents-tools.mdx)
Agent → Agent Tool: "Connect the new agent's **Toolset** port to the existing agent's **Tools** port." (Agents_agents-tools.mdx)
```
