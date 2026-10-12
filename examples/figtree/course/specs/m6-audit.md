# Module 6 capstone: The audit pack

No canvas this time. Students take a flow that already ran, export what it stored, and work through a rubric: protected health information in prompts and logs, tool scope, who may edit flows, and what leaves in an export.

## Components
- **Instructor Flow** (kind: block, icon: layers): a flow from an earlier module, run once more.
- **Message Export** (kind: store, icon: database): the stored messages and sessions, exported through the Monitor API.
- **Audit Rubric** (kind: document, icon: edit-script): the questions on PHI, tool scope, roles and export hygiene.
- **Students** (kind: actor, icon: user): work the rubric in pairs.
- **Findings** (kind: terminal, icon: residual): flagged fields, over-broad tools, retention gaps.

## Flows
Instructor Flow → Message Export → Audit Rubric → Findings
Students → Audit Rubric (data): students fill the rubric from the export.

## Steps
1. Run one earlier flow and export its session messages.
2. Hand out the audit rubric.
3. Flag every field that holds PHI and every tool that could write.
4. Try red-team prompts against a flow with a write tool, and record the mitigations.
5. Scan a flow export for keys before it goes into git.

```evidence
Instructor Flow: "Instructor demo flow" (course.md)
Message Export: "Message / session export" (course.md)
Audit Rubric: "audit-rubric.json" (course.md)
Students: "Students" (course.md)
Findings: "Document failures" (course.md)
```
