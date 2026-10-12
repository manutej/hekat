# Four parts with real contents

What each Langflow component holds for one member question.

Message path:

Chat Input -> Prompt Template
Prompt Template -> Chat Model
Chat Model -> Chat Output

Knowledge path:

Knowledge Base -> Prompt Template

Chat Input holds the member question.
Prompt Template holds standing instructions and the question.
Chat Model writes the answer from the prompt.
Chat Output shows the reply the member sees.
