# Conversation memory across turns and sessions

Langflow stores chat messages in its database under a session ID, and a flow reads them back by that ID. Build this flow when an agent should remember earlier turns of the same conversation.

## Components
- **Chat Input** (kind: terminal, icon: user): where the user's message enters the flow.
- **Session ID** (kind: document, icon: text): the identifier that groups messages into one conversation; defaults to the flow ID.
- **Langflow Storage** (kind: store, icon: database): the database where messages are saved with their session IDs.
- **Message History** (kind: block, icon: layers): retrieves stored messages by session ID, or stores new ones.
- **Prompt Template** (kind: block, icon: edit-script): puts the retrieved history into the `{memory}` variable.
- **Agent** (kind: block, icon: gear): answers using the history; its built-in chat memory is on by default.
- **Chat Output** (kind: terminal, icon: image): returns the response and passes it back to be stored.

## Flows
Chat Input → Agent → Chat Output
Session ID → Message History (data): the component uses the session ID from upstream to filter messages.
Session ID → Agent (data): the built-in memory reads messages for the same session ID.
Langflow Storage → Message History (data): messages are retrieved from Langflow storage.
Langflow Storage → Agent (data): the built-in memory reads from Langflow storage.
Message History → Prompt Template → Agent (data): the history fills the memory variable that reaches the agent.
Chat Output → Message History (data): each response is stored by a second Message History in Store mode.

## Steps
1. Pass a custom session ID in the API call, or leave it empty to use the flow ID.
2. Add a Message History component in Retrieve mode at the start of the flow.
3. Add a Prompt Template with a memory variable and connect the Message History output to it.
4. Connect the Prompt Template output to the Agent and connect Chat Input to the Agent.
5. Connect the Agent output to Chat Output.
6. Add a second Message History in Store mode and connect Chat Output to its Message input.

## Not in the documentation
- The pages do not show the Session ID as a component with ports; it is a parameter passed in the payload or set in a component's advanced settings.
- The pages describe the Prompt Template wiring with a Language Model component and say an Agent can be used instead.

```evidence
Chat Input: "Add a **Chat Input** component, and then connect it to the **Language Model** component's **Input** field." (Components_message-history.mdx)
Session ID: "Chat history and memories are grouped by [session ID (`session_id`)](/session-id)." (Develop_memory.mdx)
Langflow Storage: "Messages are stored in the database with session IDs as a reference." (Develop_session-id.mdx)
Message History: "The **Message History** component provides combined chat history and message storage functionality." (Components_message-history.mdx)
Prompt Template: "Add a **Prompt Template** component, add a `{memory}` variable to the **Template** field, and then connect the **Message History** output to the **memory** input." (Components_message-history.mdx)
Agent: "**Agent component**: This component has built-in chat memory that is enabled by default." (Develop_memory.mdx)
Chat Output: "Connect the **Language Model** component's output to a **Chat Output** component." (Components_message-history.mdx)
Chat Output → Message History: "Connect the **Chat Output** component's output to the **Message History** component's **Message** input." (Components_message-history.mdx)
```
