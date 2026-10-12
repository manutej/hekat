# Running a Flow from an Application through the API

An external application calls the Workflow API with a flow ID and an input, and gets the result back in one response, as a stream of events, or later from a queued job. Build it when a chatbot, website or script must run a Langflow flow.

## Components
- **External Application** (kind: actor, icon: user): the app, script or website that sends the request and uses the result.
- **API Access** (kind: document, icon: text): the pane under Share that generates Python, JavaScript and curl snippets for the flow.
- **Workflow API** (kind: block, icon: gear): the endpoint that runs a workflow in sync, stream or background mode.
- **Flow** (kind: block, icon: layers): the flow identified by its flow_id that the API executes.
- **Event Stream** (kind: document, icon: render): the Server-Sent Events stream of the run, in stream mode.
- **Job** (kind: process, icon: loop): the queued run created in background mode, identified by a job_id.
- **Status Endpoint** (kind: block, icon: search): the endpoint that returns the status and results of a job.

## Flows
API Access → External Application (data): the generated snippets are copied into the application.
External Application → Workflow API (control): the application sends POST /api/v2/workflows with the flow_id and input_value.
Workflow API → Flow (control): the API executes the flow in the selected mode.
Flow → Event Stream (data): in stream mode the run is emitted as events.
Event Stream → External Application (data): the application reads the events as they arrive.
Workflow API → Job (data): in background mode the API queues a job and returns a job_id.
Job → Status Endpoint (data): the job's status and results are served by the endpoint.
External Application → Status Endpoint (control): the application polls with the job_id until the job completes.

## Steps
1. Open the flow, click Share, select API access and copy the snippet for your language.
2. Set the Langflow API key in the x-api-key header.
3. Send a POST request to the Workflow API with the flow_id, the input_value and a mode.
4. In sync mode, read the answer from output.text in the response.
5. In stream mode, read the events from the stream until the run ends.
6. In background mode, poll the status endpoint with the job_id until the status is completed.

## Not in the documentation
The pages do not state how the sync response travels back from the Workflow API to the application as a separate step, so no return arrow is drawn for it.

```evidence
External Application: "Langflow provides several ways to run flows from external applications:" (Flows_concepts-publish.mdx)
API Access: "Langflow automatically generates Python, JavaScript, and curl code snippets for your flows." (Flows_concepts-publish.mdx)
Workflow API: "The Workflow API provides programmatic access to execute Langflow workflows" (API-Reference_workflows-api.mdx)
Flow: "UUID of the flow to execute." (API-Reference_workflows-api.mdx)
Event Stream: "to receive a Server-Sent Events (SSE) stream for the run." (API-Reference_workflows-api.mdx)
Job: "queue a job and receive a `job_id` immediately" (API-Reference_workflows-api.mdx)
Status Endpoint: "Retrieve the status and results of a workflow execution by job ID." (API-Reference_workflows-api.mdx)
External Application → Workflow API: "executes Langflow flows over `POST /api/v2/workflows` in three modes" (API-Reference_workflow-api-quickstart.mdx)
Workflow API → Flow: "Execute a workflow in `sync`, `stream`, or `background` mode." (API-Reference_workflows-api.mdx)
External Application → Status Endpoint: "Poll [GET /api/v2/workflows](#get-workflow-status-endpoint) for status and results" (API-Reference_workflows-api.mdx)
```
