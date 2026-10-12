# Minimal chat agent flow

Minimal agentic chat flow on the canvas.

User message path:

Chat Input -> Agent Component
Agent Component -> Chat Output

Reasoning path:

Language Model -> Agent Component

The Agent Component uses the Language Model as a reasoning engine.

Blank flow build workflow:

1. Add Agent Component to Flow Canvas
2. Add Chat Input and Chat Output
3. Connect Chat Input to Agent Component
4. Connect Agent Component to Chat Output
5. Connect Language Model to Agent Component
