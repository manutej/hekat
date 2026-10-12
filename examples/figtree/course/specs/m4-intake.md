# Module 4 capstone: Prior-authorisation intake that asks back

The flow pulls the required fields out of the member's message. If any are missing it asks a clarifying question; if all are present it submits the request to the mock service.

## Components
- **Chat Input** (kind: terminal, icon: user): the intake message.
- **Structured Output** (kind: block, icon: grid): extracts member id, procedure code and provider NPI as fields.
- **Fields Missing** (kind: decision, icon: split): checks whether every required field is present.
- **Clarify** (kind: block, icon: bolt): a chat model that asks only for what is missing.
- **Submit Intake** (kind: block, icon: render): an API Request that posts the complete request.
- **Chat Output** (kind: terminal, icon: text): either the clarifying question or the confirmation.

## Flows
Chat Input → Structured Output → Fields Missing
Fields Missing → Clarify (control): when a field is missing.
Fields Missing → Submit Intake (control): when the request is complete.
Clarify → Chat Output
Submit Intake → Chat Output

## Steps
1. Add Structured Output with the three required fields.
2. Add a conditional router on "any field missing".
3. On the missing branch, a chat model asks the clarifying question.
4. On the complete branch, an API Request submits to the mock service.
5. Test with the incomplete fixture and watch the clarify branch fire.

```evidence
Chat Input: "Chat Input" (course.md)
Structured Output: "Structured Output" (course.md)
Fields Missing: "Fields missing?" (course.md)
Clarify: "clarify prompt" (course.md)
Submit Intake: "POST mock prior-auth" (course.md)
Chat Output: "Chat Output" (course.md)
```
