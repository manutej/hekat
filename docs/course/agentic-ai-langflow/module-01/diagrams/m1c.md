# Where the API key lives

The provider key stays on the class server, never in the browser.

Request path:

Student Browser -> Class Portal
Class Portal -> Langflow
Langflow -> Model Provider

Student Browser holds no provider key.
Class Portal holds the provider key and adds the student session id.
Langflow runs the published flow.
Model Provider receives the key with each call.
