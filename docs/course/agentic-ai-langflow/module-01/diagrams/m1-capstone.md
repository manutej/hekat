# Member Benefits FAQ capstone

Module 1 capstone flow for the Member Benefits FAQ lab.

Member path:

Chat Input -> Prompt Template
Prompt Template -> Chat Model
Chat Model -> Chat Output

Knowledge path:

Knowledge Base -> Prompt Template

Chat Input receives the member question.
Prompt Template holds system instructions and limits.
Knowledge Base optionally adds plan document passages to the prompt.
Chat Model writes the grounded answer.
Chat Output shows the reply.

Capstone build workflow:

1. Add Chat Input and Chat Output
2. Write the system prompt in Prompt Template
3. Connect OpenRouter Chat Model with key on server only
4. Optionally connect Knowledge Base of plan documents
5. Publish and test PPO versus HMO questions
