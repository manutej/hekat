# Member Benefits FAQ capstone

Capstone flow for lab m1-l01 Member Benefits FAQ.

Chat Input -> Prompt Template
Prompt Template -> Chat Model
Chat Model -> Chat Output

Knowledge Base -> Prompt Template

Chat Input receives the member question.
Prompt Template holds system instructions and limits.
Knowledge Base adds plan document passages to the prompt when connected.
Chat Model writes the grounded answer.
Chat Output shows the reply.

Capstone build workflow:

1. Add Chat Input and Chat Output
2. Write the system prompt in Prompt Template
3. Connect Chat Model with API key on server only
4. Optionally connect Knowledge Base
5. Publish and test across turns
