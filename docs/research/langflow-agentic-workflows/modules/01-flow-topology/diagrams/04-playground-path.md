# Playground execution path

The Playground runs the flow for interactive testing.

Playground workflow:

1. Open Playground from flow editor
2. Send prompt via Chat Input
3. Agent Component calls Language Model
4. Response appears on Chat Output

Canvas data path:

Chat Input -> Agent Component
Language Model -> Agent Component
Agent Component -> Chat Output
