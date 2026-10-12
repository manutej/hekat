# Crosswalk FAQ chain and Agent Component flow

Unified view: the course FAQ capstone is the same hub pattern as Langflow agentic docs.

User path:

Chat Input -> Agent Component
Agent Component -> Chat Output

Course naming feeds the hub:

Prompt Template -> Agent Component
Knowledge Base -> Agent Component

Langflow doc naming feeds the hub:

Language Model -> Agent Component

Prompt Template maps to Agent instructions.
Chat Model maps to Language Model.
Knowledge Base maps to retrieval context on the Agent Component.
