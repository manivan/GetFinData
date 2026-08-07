---
name: write-plan
description: Convert spec to an actionable implementation plan in workflow-docs/plans/<feature>.plan.md.
model: claude-opus-4.6
---

Spec path:
${input:spec:workflow-docs/specs/<feature>.spec.md}

Plan path:
${input:plan:workflow-docs/plans/<feature>.plan.md}

Before writing the plan, verify the work is suitable for vertical slicing:

1. Is there user-visible behavior to deliver?
2. Can a thin path through all layers be demoed end-to-end?
3. Is each candidate slice independently shippable?

If any answer is "no," STOP. Explain why vertical slicing does not fit and recommend an alternative (phased migration, spike, `/request-refactor-plan`, or a single PR). Wait for the user to confirm the alternative or explicitly say "force vertical anyway" before continuing.

If clarifying questions about scope, slicing, or risk exceed ~3, create a question file per the "Question Files" section in `.github/copilot-instructions.md` (path: `workflow-docs/questions/<feature>.write-plan-questions.md`) instead of asking in chat. When the user signals the file is complete, validate, ingest into the plan (making the plan self-contained), then auto-archive per the same section.

Create an implementation plan with:
- Steps (ordered)
- Files to change (anticipated)
- Checkpoints (where to run tests)
- Risks + mitigations
- Acceptance Criteria -> Verification mapping

After writing the plan, append an entry to `workflow-docs/audit.md` with: timestamp, phase (`write-plan`), user request summary, assistant action summary, artifacts created/updated, key risks/decisions, and next step.

Read `workflow-docs/workflow-state.md` at the start of this prompt and update it at the end: set Current Phase to `Write Plan`, set Active Artifact to the new plan path, refresh Current Feature, Current Objective, Next Immediate Action (`/execute-plan`), Last Updated, Last Prompt Run, and tick the Write Plan / Issues checkbox.