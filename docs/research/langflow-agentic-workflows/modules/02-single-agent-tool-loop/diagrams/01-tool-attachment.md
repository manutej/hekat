# Tool attachment workflow

Agents register tools as Tool objects the Agent Component reads at initialization.

Tool attachment path:

Toolset Port -> Agent Component Tools Port
Chat Input -> Agent Component

Tool attachment workflow:

1. Enable Tool Mode on a tool component
2. Connect Toolset port to Agent Component Tools port
3. Send user prompt through Chat Input
