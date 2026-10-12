# Module 1 capstone: Member Benefits FAQ

A member asks a question in plain words; the agent answers from a system prompt and, optionally, from a small knowledge base of plan documents.

## Components
- **Chat Input** (kind: terminal, icon: user): the member's question arrives here.
- **Prompt Template** (kind: document, icon: edit-script): the system prompt that sets the agent's tone and limits.
- **Knowledge Base** (kind: store, icon: database): optional plan documents the agent can look up.
- **Chat Model** (kind: block, icon: bolt): the language model (OpenRouter) that writes the answer.
- **Chat Output** (kind: terminal, icon: text): the reply the member sees.

## Flows
Chat Input → Prompt Template → Chat Model → Chat Output
Knowledge Base → Prompt Template (data): retrieved passages are added to the prompt.

## Steps
1. Add Chat Input and Chat Output.
2. Write the system prompt in a Prompt Template.
3. Connect an OpenRouter chat model; keep the API key on the server, never in a browser.
4. Optionally add a knowledge base of plan documents.
5. Publish, then test PPO versus HMO questions across several turns.

```evidence
Chat Input: "Chat Input" (course.md)
Prompt Template: "Prompt Template" (course.md)
Knowledge Base: "Knowledge retrieval" (course.md)
Chat Model: "OpenRouter Chat Model" (course.md)
Chat Output: "Chat Output" (course.md)
```
