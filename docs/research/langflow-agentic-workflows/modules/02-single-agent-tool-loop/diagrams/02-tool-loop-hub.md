# Single-agent tool loop

Control and data paths during a Playground run with multiple tools.

User path:

Chat Input -> Agent Component
Agent Component -> Chat Output

Tool feeds into the agent:

Web Search Component -> Agent Component
URL Component -> Agent Component
Calculator Component -> Agent Component

Playground events include the input message, each tool call, streaming tokens, and the final answer.
