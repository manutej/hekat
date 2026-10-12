# Custom Language Model port

When the global Model Providers list is not enough, attach a language model component on the canvas.

Placement workflow:

1. Add Custom Language Model Component left of Agent Component
2. Connect output to Language Model port

Canvas wiring (left to right):

Custom Language Model Component -> Agent Component
Agent Component -> Chat Output

The Language Model port on Agent Component receives the Custom Language Model Component connection.
