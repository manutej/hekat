# Four parts with real contents (course narrative)

What each part holds for one real member question (Silver PPO MRI example).

Layout: horizontal row of four large panels (Chat Input, Prompt Template, Chat Model, Chat Output), each with icon, bold component label, grey intro line, and nested white example box with quoted member or model text. Optional Knowledge Base panel below Prompt Template with upward arrow labelled as passages added to the prompt.

Chat Input -> Prompt Template
Prompt Template -> Chat Model
Chat Model -> Chat Output
Knowledge Base -> Prompt Template

Chat Input holds the member question exactly as typed, for example: "Is an MRI covered on the Silver PPO?"
Prompt Template holds standing instructions then the question, for example instructions to answer only from plan documents.
Chat Model reads instructions, documents, and question together and writes one reply.
Chat Output shows the reply the member sees.
Knowledge Base holds optional plan document passages fed into the prompt.

Only the Prompt Template is written by you; other parts are standard Langflow components you connect.
