# Module 5 capstone: A specialist approves the appeal

The model drafts an appeal packet, then the flow pauses. A specialist approves or rejects. Only an approved draft is submitted; a rejected one goes back for another draft, and the member sees a pending message meanwhile.

## Components
- **Chat Input** (kind: terminal, icon: user): the denial case the member describes.
- **Draft Packet** (kind: block, icon: bolt): a chat model that writes the appeal summary.
- **Human Input** (kind: decision, icon: check): the specialist's Approve or Reject decision.
- **Submit Appeal** (kind: block, icon: render): an API Request to the mock appeal service.
- **Chat Output** (kind: terminal, icon: text): the confirmation, or the pending notice while review waits.

## Flows
Chat Input → Draft Packet → Human Input
Human Input → Submit Appeal (control): the Approve branch.
Human Input → Draft Packet (feedback): the Reject branch asks for a new draft.
Submit Appeal → Chat Output
Human Input → Chat Output (control): the member is told that review is pending.

## Steps
1. Add a chat model that drafts the appeal packet.
2. Add a Human Input component with Approve and Reject actions.
3. Wire only the Approve branch to the submission request.
4. Wire Reject back to the drafting model.
5. Run it: the flow pauses at the gate and resumes without re-running finished steps.

```evidence
Chat Input: "Chat Input" (course.md)
Draft Packet: "draft packet" (course.md)
Human Input: "Human Input" (course.md)
Submit Appeal: "mock submit" (course.md)
Chat Output: "Chat Output" (course.md)
```
