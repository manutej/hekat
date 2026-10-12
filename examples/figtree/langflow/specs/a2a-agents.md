# Agents talking to agents over A2A

Langflow can publish a flow as an A2A agent that A2A clients discover and call, and a flow can call a remote A2A agent through a calling component. Build it to expose an agent to other systems or to reuse one that lives elsewhere.

## Components
- **A2A Client** (kind: actor, icon: user): an outside caller that discovers and calls the published agent.
- **Published Flow** (kind: block, icon: layers): a flow with chat input and output, served as an A2A agent after Save.
- **Agent Card** (kind: document, icon: document): the JSON file clients fetch to learn what the agent does.
- **JSON-RPC Endpoint** (kind: block, icon: ports): receives message/send and other calls and runs the flow.
- **Chat Input** (kind: terminal, icon: text): supplies the message to the calling component.
- **A2A Caller** (kind: block, icon: gear): the component that calls an A2A agent and returns its reply.
- **Remote A2A** (kind: actor, icon: grounder): an A2A agent called by URL, or a published flow in the same project.
- **Chat Output** (kind: terminal, icon: image): receives the Response output of the caller.

## Flows
Published Flow → Agent Card (data): Langflow serves the card when the flow is published.
A2A Client → Agent Card (data): clients fetch the card for discovery.
A2A Client → JSON-RPC Endpoint (control): the client sends message/send to the endpoint.
JSON-RPC Endpoint → Published Flow (control): a message/send request runs the flow.
Chat Input → A2A Caller → Chat Output
A2A Caller → Remote A2A (control): the component calls the agent in Internal or External mode.

## Steps
1. Set LANGFLOW_A2A_ENABLED to true before starting Langflow.
2. Open a flow that has Chat Input and Chat Output and turn on Serve as an A2A agent in the Agent tab.
3. Click Save so the status changes to Live and the card and endpoint are served.
4. Send a message from an A2A client to the JSON-RPC endpoint and read the reply.
5. In another flow, add the calling component and set Mode to Internal or External.
6. Connect Chat Input to the Message input and the Response output to Chat Output.

## Not in the documentation
The pages do not describe how the Remote A2A agent runs internally or how the caller negotiates with it beyond the URL and the reply. OAuth is not supported for A2A as of Langflow 1.11.x.

```evidence
A2A Client: "This page describes how to publish a flow as an A2A agent that A2A clients can discover and call." (Agents_a2a-server.mdx)
Published Flow: "To publish the flow, click **Save**." (Agents_a2a-server.mdx)
Agent Card: "an **agent card** is a JSON file that clients fetch to learn what the agent does and how to communicate with it" (Agents_a2a-server.mdx)
JSON-RPC Endpoint: "Only the JSON-RPC endpoint enforces authentication." (Agents_a2a-server.mdx)
Chat Input: "Connect a [**Chat Input** component](./chat-input-and-output#chat-input) to the **A2A Agent** component's **Message** input." (Components_a2a-agent.mdx)
A2A Caller: "The **A2A Agent** component calls an [Agent2Agent (A2A)](https://a2a-protocol.org/) agent and returns its reply." (Components_a2a-agent.mdx)
Remote A2A: "use **External** mode to call a remote A2A agent by its published URL" (Components_a2a-agent.mdx)
Chat Output: "Connect the **Response** output to the next component in your flow, such as a [**Chat Output** component](./chat-input-and-output#chat-output)." (Components_a2a-agent.mdx)
A2A Client → JSON-RPC Endpoint: "To send a message, use the JSON-RPC URL from the **Address** tab, and not the agent card URL." (Agents_a2a-server.mdx)
JSON-RPC Endpoint → Published Flow: "A `message/send` request runs the flow and returns a completed task carrying the agent's reply as a text artifact." (Agents_a2a-server.mdx)
A2A Caller → Remote A2A: "or call out to any remote spec-compliant A2A agent" (Agents_a2a-server.mdx)
```
