---
name: prd-to-issues
description: Break a PRD into independently-grabbable local implementation tickets using tracer-bullet vertical slices. Use when user wants to convert a PRD to issues, create implementation tickets, or break down a PRD into work items.
model: claude-opus-4.6
---

# PRD to Issues

Break a PRD into independently-grabbable local implementation tickets using vertical slices (tracer bullets).

## Process

### 0. Suitability check

Before proceeding, verify the work is suitable for vertical slicing:

1. Is there user-visible behavior to deliver?
2. Can a thin path through all layers be demoed end-to-end?
3. Is each candidate slice independently shippable?

If any answer is "no," STOP. Explain why vertical slicing does not fit and recommend an alternative (phased migration, spike, `/request-refactor-plan`, or a single PR). Wait for the user to confirm the alternative or explicitly say "force vertical anyway" before continuing.

### 1. Locate the PRD

Ask the user for the local PRD markdown path (for example: `workflow-docs/specs/<feature>.prd.md`).

If the PRD is not already in your context window, read it from the provided local file path.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

### 3. Draft vertical slices

Break the PRD into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories from the PRD this addresses

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

If the breakdown requires more than ~3 batched clarifications, create a question file per the "Question Files" section in `.github/copilot-instructions.md` (path: `workflow-docs/questions/<feature>.prd-to-issues-questions.md`) instead of asking in chat. When the user signals the file is complete, validate, ingest into the issues backlog (making it self-contained), then auto-archive per the same section.

### 5. Create local issue entries

For each approved slice, create or update a local issue backlog markdown file at `workflow-docs/specs/<feature>.issues.md`. Use the issue body template below.

Create ticket entries in dependency order (blockers first) so you can reference local IDs in the "Blocked by" field.

Use a deterministic local ID format such as `FSM-001`, `FSM-002`, etc.

<issue-template>
## Local Ticket ID

<feature-prefix>-<number>

## Parent PRD

workflow-docs/specs/<feature>.prd.md

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- Blocked by <feature-prefix>-<number> (if any)

Or "None - can start immediately" if no blockers.

## User stories addressed

Reference by number from the parent PRD:

- User story 3
- User story 7

</issue-template>

Do NOT modify the parent PRD content while generating local tickets. Only reference it.

### 6. Append an audit entry

Append an entry to `workflow-docs/audit.md` with: timestamp, phase (`prd-to-issues`), user request summary, assistant action summary, artifacts created/updated, ticket IDs generated, dependency summary, and next step.

### 7. Update workflow state

Read `workflow-docs/workflow-state.md` at the start of this prompt and update it at the end: set Current Phase to `Write Plan`, set Active Artifact (Issues) to the new issues file path, seed the Execution Progress table with one row per ticket (status `pending`), refresh Current Feature, Current Objective, Next Immediate Action (`/execute-plan`), Last Updated, Last Prompt Run, and tick the Write Plan / Issues checkbox.
