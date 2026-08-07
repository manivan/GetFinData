---
name: brainstorm
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me" or "brainstorm".
model: claude-opus-4.6
---
Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

If a question can be answered by exploring the codebase, explore the codebase instead.

Be sure to continue asking questions until there are no outstanding questions or ambiguities in the spec.

There should be no open questions or ambiguities left at the end of this process.

Follow the "Structured Reasoning Protocol" in `.github/copilot-instructions.md`.

If clarifying questions exceed ~3 or the answers will gate the downstream PRD/spec, create a question file per the "Question Files" section in `.github/copilot-instructions.md` (path: `workflow-docs/questions/<feature>.brainstorm-questions.md`) instead of asking in chat. When the user signals the file is complete, validate, ingest into your understanding (and any artifact being produced), then auto-archive per the same section.

Before starting, read `workflow-docs/workflow-state.md` to ground in current state.

At the end:
- Append an entry to `workflow-docs/audit.md` capturing: timestamp, phase (`brainstorm`), user request summary, key decisions resolved, artifacts updated (if any), and next step.
- Update `workflow-docs/workflow-state.md`: set Current Phase to `Brainstorm` (mark complete on exit), refresh Current Feature, Current Objective, Next Immediate Action, Last Updated, Last Prompt Run, and tick the Brainstorm checkbox.

