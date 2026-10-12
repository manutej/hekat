# Branching, looping and sub-flows inside a flow

If-Else and Smart Router send a message down one branch, Loop repeats a chain of components for every item in a list, and Run Flow runs another flow as a step. Build them when one linear path is not enough.

## Components
- **Loop** (kind: process, icon: loop): iterates over a list, sending one item at a time out of the Item port and the aggregated result out of the Done port.
- **Type Convert** (kind: block, icon: gear): in the CSV example, turns each row into a Message.
- **Structured Output** (kind: block, icon: layers): turns each Message into structured data and returns it to the Loop.
- **Chroma DB** (kind: store, icon: database): receives the aggregated list from the Done port.
- **If-Else** (kind: decision, icon: split): routes a message to True or False by comparing two strings.
- **Smart Router** (kind: decision, icon: tree): the LLM-powered variation of If-Else that routes by category.
- **Language Model** (kind: block, icon: bolt): categorizes input for the Smart Router, or answers on the True branch of the If-Else.
- **Run Flow** (kind: process, icon: merge): runs another Langflow flow as a subprocess of the current flow.
- **Agent** (kind: actor, icon: wrench): can run a Run Flow component as a tool.

## Flows
Loop → Type Convert → Structured Output (control): the Item port passes each row through the chain.
Structured Output → Loop (control): the last component in the chain returns to the Looping port for the next item.
Loop → Chroma DB (control): when no items are left, the Done port sends the aggregated result on.
If-Else → Language Model (control): the True output port connects to the Language Model Input port.
Smart Router → Language Model (control): the Smart Router uses the connected model to pick a route.
Agent → Run Flow (control): the agent runs the subflow as a tool.

## Steps
1. Connect a list such as a CSV file to the Loop component.
2. Connect the Item port to one chain of components and connect the last component back to the Looping port.
3. Connect the Done port to the component that receives the aggregated result.
4. Use If-Else with an operator and match text to send a message down the True or False port.
5. Use Smart Router with a Routes table and a Language Model to route by category.
6. Add Run Flow and select the flow to run, or attach it to an Agent as a tool.

## Not in the documentation
- The pages do not name the component that follows the Positive, Negative or Neutral ports of the Smart Router.
- The pages say the If-Else component is not compatible with the Loop component, and give no flow between them.
- The pages do not name the component that receives the Run Flow outputs.

```evidence
Loop: "The **Loop** component iterates over a list of input by passing individual items to other components attached at the **Item** output port" (Components_loop.mdx)
Type Convert: "the **Item** port passes each row to a **Type Convert** component to convert the row into a `Message` object" (Components_loop.mdx)
Structured Output: "passes the `Message` to a **Structured Output** component to be processed into structured data" (Components_loop.mdx)
Chroma DB: "loads the aggregated list of structured data into a Chroma DB database through the **Chroma DB** component connected to the **Done** port" (Components_loop.mdx)
If-Else: "The **If-Else** component is a conditional router that routes messages by comparing two strings." (Components_if-else.mdx)
Smart Router: "The **Smart Router** component is an LLM-powered variation of the [**If-Else** component](/if-else)." (Components_smart-router.mdx)
Language Model: "the **Smart Router** uses a connected [**Language Model** component](/components-models) to categorize and route incoming messages." (Components_smart-router.mdx)
Run Flow: "The **Run Flow** component runs another Langflow flow as a subprocess of the current flow." (Components_run-flow.mdx)
Agent: "attach flows to [**Agent** components](/components-agents) as [tools for agents](/agents-tools) to run as needed" (Components_run-flow.mdx)
Loop → Type Convert: "the **Item** port passes each row to a **Type Convert** component to convert the row into a `Message` object" (Components_loop.mdx)
Type Convert → Structured Output: "passes the `Message` to a **Structured Output** component to be processed into structured data" (Components_loop.mdx)
Structured Output → Loop: "The final component in the **Item** loop connects back to the **Loop** component's **Looping** port to process the next item." (Components_loop.mdx)
Loop → Chroma DB: "the **Loop** component passes the aggregated result of all looping to the component connected to the **Done** port." (Components_loop.mdx)
If-Else → Language Model: "Connect the **If-Else** component's **True** output port to the **Language Model** component's **Input** port." (Components_if-else.mdx)
Smart Router → Language Model: "the **Smart Router** uses a connected [**Language Model** component](/components-models) to categorize and route incoming messages." (Components_smart-router.mdx)
Agent → Run Flow: "attach flows to [**Agent** components](/components-agents) as [tools for agents](/agents-tools) to run as needed" (Components_run-flow.mdx)
```
