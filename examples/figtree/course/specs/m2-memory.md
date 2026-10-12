# Module 2 capstone: Remember the plan type

The member says "HDHP" once; two turns later a deductible question is answered for an HDHP without asking again, because the conversation is stored under the member's session.

## Components
- **Chat Input** (kind: terminal, icon: user): each turn of the conversation.
- **Message History** (kind: store, icon: database): the stored turns for this session, the last ten by default.
- **Prompt Template** (kind: document, icon: edit-script): places the remembered plan type in context.
- **Chat Model** (kind: block, icon: bolt): answers with the history in view.
- **Chat Output** (kind: terminal, icon: text): the reply, which is stored too.

## Flows
Chat Input → Prompt Template → Chat Model → Chat Output
Message History → Chat Model (data): prior turns for the same session id reach the model.
Chat Output → Message History (feedback): every reply is stored for the next turn.

## Steps
1. Add a Message History component next to the Chat Model.
2. Keep a window of ten turns.
3. Give every student their own session id, so conversations never mix.
4. Ask "I have an HDHP", then "What is my deductible?" and watch it remember.

```evidence
Chat Input: "Chat Input" (course.md)
Message History: "Message History" (course.md)
Prompt Template: "Prompt Template" (course.md)
Chat Model: "Chat Model" (course.md)
Chat Output: "Chat Output" (course.md)
```
