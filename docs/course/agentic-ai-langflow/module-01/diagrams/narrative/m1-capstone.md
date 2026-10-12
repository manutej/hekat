# Module 1 capstone: Member Benefits FAQ (course narrative)

Capstone Langflow layout for lab m1-l01 Member Benefits FAQ with readable panel art.

Show Chat Input, Prompt Template, Chat Model, and Chat Output in clear left-to-right flow with a Knowledge Base side feed into Prompt Template. Include a short section title and one-line captions under each component name where space allows.

Chat Input -> Prompt Template
Prompt Template -> Chat Model
Chat Model -> Chat Output
Knowledge Base -> Prompt Template

Chat Input receives the member question.
Prompt Template holds system instructions and limits (system prompt).
Knowledge Base adds plan document passages to the prompt when connected.
Chat Model writes the grounded answer.
Chat Output shows the reply.

Capstone build: add Chat Input and Chat Output; write system prompt in Prompt Template; connect Chat Model with API key on server only; optionally connect Knowledge Base; publish and test across turns.
