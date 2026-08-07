---
name: prd-to-plan
description: Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices, saved as a local markdown file in workflow-docs/plans/. Use when user wants to break down a PRD, create an implementation plan, plan phases from a PRD, or mentions "tracer bullets".
model: claude-opus-4.6
---

# PRD to Plan

Break a PRD into a phased implementation plan using vertical slices (tracer bullets). Output is a markdown file in `workflow-docs/plans/`.

## Process

### 0. Suitability check

Before proceeding, verify the work is suitable for vertical slicing:

1. Is there user-visible behavior to deliver?
2. Can a thin path through all layers be demoed end-to-end?
3. Is each candidate slice independently shippable?

If any answer is "no," STOP. Explain why vertical slicing does not fit and recommend an alternative (phased migration, spike, `/request-refactor-plan`, or a single PR). Wait for the user to confirm the alternative or explicitly say "force vertical anyway" before continuing.

### 1. Confirm the PRD is in context

The PRD should already be in the conversation. If it isn't, ask the user to paste it or point you to the file.

### 2. Explore the codebase

If you have not already explored the codebase, do so to understand the current architecture, existing patterns, and integration layers.

### 3. Identify durable architectural decisions

Before slicing, identify high-level decisions that are unlikely to change throughout implementation:

- Route structures / URL patterns
- Database schema shape
- Key data models
- Authentication / authorization approach
- Third-party service boundaries

These go in the plan header so every phase can reference them.

### 4. Draft vertical slices

Break the PRD into **tracer bullet** phases. Each phase is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
- Do NOT include specific file names, function names, or implementation details that are likely to change as later phases are built
- DO include durable decisions: route paths, schema shapes, data model names
</vertical-slice-rules>

### 5. Quiz the user

Present the proposed breakdown as a numbered list. For each phase show:

- **Title**: short descriptive name
- **User stories covered**: which user stories from the PRD this addresses

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Should any phases be merged or split further?

Iterate until the user approves the breakdown.

If the breakdown requires more than ~3 batched clarifications, create a question file per the "Question Files" section in `.github/copilot-instructions.md` (path: `workflow-docs/questions/<feature>.prd-to-plan-questions.md`) instead of asking in chat. When the user signals the file is complete, validate, ingest into the plan (making the plan self-contained), then auto-archive per the same section.

### 6. Write the plan file

Create `workflow-docs/plans/` if it doesn't exist. Write the plan as a markdown file named after the feature (e.g. `workflow-docs/plans/user-onboarding.plan.md`). Use the template below.

<plan-template>
# Plan: <Feature Name>

> Source PRD: <brief identifier or link>

## Architectural decisions

Durable decisions that apply across all phases:

- **Routes**: ...
- **Schema**: ...
- **Key models**: ...
- (add/remove sections as appropriate)

---

## Phase 1: <Title>

**User stories**: <list from PRD>

### What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

### Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Phase 2: <Title>

**User stories**: <list from PRD>

### What to build

...

### Acceptance criteria

- [ ] ...

<!-- Repeat for each phase -->
</plan-template>

### 7. Append an audit entry

Append an entry to `workflow-docs/audit.md` with: timestamp, phase (`prd-to-plan`), user request summary, assistant action summary, artifacts created/updated, approved phase breakdown summary, and next step.

### 8. Update workflow state

Read `workflow-docs/workflow-state.md` at the start of this prompt and update it at the end: set Current Phase to `Write Plan`, set Active Artifact (Plan) to the new plan path, seed the Execution Progress table with one row per phase (status `pending`), refresh Current Feature, Current Objective, Next Immediate Action (`/execute-plan`), Last Updated, Last Prompt Run, and tick the Write Plan / Issues checkbox.
