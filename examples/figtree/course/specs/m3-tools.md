# Module 3 capstone: Claims status, read only

The agent reads a question, decides which tool answers it, calls a mock claims service and replies with what it found. Tools only read; nothing is paid or changed.

## Components
- **Chat Input** (kind: terminal, icon: user): "What is the status of my claim?"
- **Agent** (kind: block, icon: gear): decides which tool to call and writes the reply.
- **Claims Lookup** (kind: block, icon: search): an API Request in Tool Mode that reads a claim by member id.
- **Prior Auth Lookup** (kind: block, icon: document): a second tool that reads a prior-authorisation by id.
- **Mock Claims API** (kind: store, icon: database): the practice service with fixture members.
- **Chat Output** (kind: terminal, icon: text): the answer, with the status it read.

## Flows
Chat Input → Agent → Chat Output
Agent → Claims Lookup (control): the agent calls the claims tool when the question is about a claim.
Agent → Prior Auth Lookup (control): the agent calls the prior-auth tool when the question names a PA.
Claims Lookup → Mock Claims API (data): the tool reads from the practice service.
Prior Auth Lookup → Mock Claims API (data): so does the second tool.

## Steps
1. Add an Agent and connect Chat Input and Chat Output.
2. Add two API Request components pointed at the mock service.
3. Turn on Tool Mode on each and connect their Toolset port to the Agent's Tools port.
4. Describe each tool as read-only in its description.
5. Ask about member M1001 and prior-auth PA-9001.

```evidence
Chat Input: "Chat Input" (course.md)
Agent: "Agent" (course.md)
Claims Lookup: "claims_lookup" (course.md)
Prior Auth Lookup: "prior_auth_lookup" (course.md)
Mock Claims API: "Mock API :3860" (course.md)
Chat Output: "Chat Output" (course.md)
```
