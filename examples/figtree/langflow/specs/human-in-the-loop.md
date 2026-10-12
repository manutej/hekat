# Pausing a Flow for a Human

Human-in-the-Loop pauses a flow, creates a checkpoint and waits for a human decision. Build it when a step, such as committing code, must be approved before the run continues.

## Components
- **Agent** (kind: actor, icon: gear): drafts the code and can be set to require approval for its tools.
- **Human Input** (kind: decision, icon: split): pauses the flow and creates one output branch per User Action.
- **Git Commit** (kind: block, icon: wrench): the tool that commits code to Git, gated by Requires approval.
- **Chat Output** (kind: terminal, icon: document): the alternate path that explains a rejection.
- **Playground** (kind: actor, icon: user): where the human selects an action in the approval pane.

## Flows
Agent → Human Input: the draft reaches the gate after the code generation steps.
Human Input → Git Commit (control): the Approve branch continues to the commit step.
Human Input → Chat Output (control): the Reject branch runs an alternate path.
Agent → Git Commit (control): the run pauses when the agent tries to call a tool that requires approval.
Playground → Human Input (control): the human's chosen action resumes the flow.

## Steps
1. Add a Human Input component after the code generation steps.
2. Enter Form Content and keep the Approve and Reject User Actions.
3. Connect the Approve output to the commit step and the Reject output to an alternate path.
4. Optionally enable Requires approval on the Git commit tool of the Agent.
5. Run the flow in the Playground and select an action in the approval pane.

## Not in the documentation
The pages do not say that Notify and Listen are part of a human approval gate. They do not name the component that revises a rejected draft, so no revision loop is drawn.

```evidence
Agent: "For example, imagine you're building an agent that drafts Python code" (Flows_human-in-the-loop.mdx)
Human Input: "The **Human Input** component pauses the flow where you place the component, and creates one output branch per configured **User Action**." (Flows_human-in-the-loop.mdx)
Git Commit: "The **Agent** tool approval enables **Requires approval** on the Git commit tool _only_." (Flows_human-in-the-loop.mdx)
Chat Output: "Connect the **Reject** output to an alternate path, such as a" (Components_human-input.mdx)
Playground: "When execution reaches the **Human Input** node, select an action in the approval pane to resume the flow." (Components_human-input.mdx)
Human Input → Git Commit: "If a human selects **Approve**, the flow continues to the commit step" (Flows_human-in-the-loop.mdx)
Human Input → Chat Output: "Connect the **Reject** output to an alternate path" (Components_human-input.mdx)
Agent → Git Commit: "The run pauses when the agent tries to call that tool, but doesn't add a branch." (Flows_human-in-the-loop.mdx)
Playground → Human Input: "select an action in the approval pane to resume the flow" (Components_human-input.mdx)
```
