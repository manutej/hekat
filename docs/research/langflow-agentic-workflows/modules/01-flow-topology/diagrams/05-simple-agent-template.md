# Simple Agent template layout

The Simple Agent quickstart template wires chat I/O plus two tools.

Template wiring:

Chat Input -> Agent Component
Agent Component -> Chat Output
Calculator Component -> Agent Component
URL Component -> Agent Component

The Agent Component selects Calculator Component or URL Component when the prompt requires math or fetched content.
