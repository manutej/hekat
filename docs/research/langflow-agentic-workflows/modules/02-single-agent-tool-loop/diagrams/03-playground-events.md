# Playground run events

Langflow event stream for one agent run with tools.

Playground Run -> Input Message Event
Playground Run -> Tool Call Event
Playground Run -> Streaming Tokens Event
Playground Run -> Final Answer Event
Final Answer Event -> Chat History

When the run finishes, Langflow writes the completed message to chat history.
