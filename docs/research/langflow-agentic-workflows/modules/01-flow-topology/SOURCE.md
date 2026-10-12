# Module 01 — Langflow flow topology

Deep teaching source for FigTree. See CITATIONS.md.

## Flow canvas and components

A Langflow **flow** is a visual graph on the **Flow Canvas**. Each **Component** exposes **ports** for inputs and outputs. Components connect when a port on one component links to a port on another.

Canvas mental model:

Flow Canvas -> Component
Component -> Port
Port -> Port

## Minimal chat agent flow

A minimal agentic chat flow uses four named components on the canvas.

User message path:

Chat Input -> Agent Component
Agent Component -> Chat Output

Reasoning engine path:

Language Model -> Agent Component

The Agent Component uses the Language Model as a reasoning engine. The Agent Component returns a Response on the Chat Output component.

Blank flow build workflow:

1. Click New Flow and select Blank Flow
2. Add Agent Component to Flow Canvas
3. Add Chat Input and Chat Output components
4. Connect Chat Input to Agent Component
5. Connect Agent Component to Chat Output
6. Connect Language Model to Agent Component Language Model port

## Model Providers and Language Model selection

Global model configuration lives in Settings under Model Providers.

Configuration workflow:

1. Open Settings Model Providers pane
2. Select Provider and enter API Key
3. Enable Language Models for that provider
4. Select model in Agent Component Language Model dropdown

Global model configuration chain:

Model Providers Pane -> Provider
Provider -> API Key Field
Enabled Language Model -> Agent Component

Alternate Language Model port:

Custom Language Model Component -> Agent Component

## Playground execution path

The Playground runs the flow on the Langflow server for interactive testing.

Playground workflow:

1. Open Playground from the flow editor
2. Send prompt through Chat Input
3. Agent Component calls Language Model
4. Agent Component writes Response to Chat Output

Playground data path (left-to-right on canvas):

Chat Input -> Agent Component
Language Model -> Agent Component
Agent Component -> Chat Output

## Simple Agent template layout

The Simple Agent template from the quickstart adds tool components on the canvas.

Template wiring:

Chat Input -> Agent Component
Agent Component -> Chat Output
Calculator Component -> Agent Component
URL Component -> Agent Component
