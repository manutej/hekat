# The six-module journey

Each module builds one working agent in a health-plan setting, from a first chatbot to a reviewed, audited assistant.

## Components
- **Introduction** (kind: terminal, icon: user): your first published agent answers member questions.
- **Components** (kind: block, icon: layers): memory, variables and a knowledge base make it remember.
- **Tools and MCP** (kind: block, icon: wrench): the agent looks up claims through tools.
- **Applications** (kind: block, icon: decompose): intake flows that check, branch and ask back.
- **Collaboration** (kind: block, icon: check): a human approves before anything leaves the building.
- **Ethics and Security** (kind: terminal, icon: eye): audit what the agent stores and may do.

## Flows
Introduction → Components → Tools and MCP → Applications → Collaboration → Ethics and Security

## Steps
1. Build and publish a member-benefits FAQ agent.
2. Give it memory so it remembers the plan type across turns.
3. Connect read-only tools for claim and prior-authorisation status.
4. Build an intake flow that asks for what is missing.
5. Put a specialist's approval in front of the appeal submission.
6. Audit prompts, logs, tools and exports.

```evidence
Introduction: "Introduction" (course.md)
Components: "Components" (course.md)
Tools and MCP: "Tools and MCP" (course.md)
Applications: "Applications" (course.md)
Collaboration: "Collaboration" (course.md)
Ethics and Security: "Ethics and Security" (course.md)
```
