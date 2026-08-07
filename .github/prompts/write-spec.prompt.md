---
name: write-spec
description: Write a detailed spec doc to workflow-docs/specs/<feature>.spec.md.
model: claude-opus-4.6
---

Read:
- `docs/_knowledge/index.md`
- any relevant knowledge files under `docs/_knowledge/**`

Spec file path:
${input:path:workflow-docs/specs/<feature>.spec.md}

If clarifying questions exceed ~3 or are required to fix open questions/ambiguities, create a question file per the "Question Files" section in `.github/copilot-instructions.md` (path: `workflow-docs/questions/<feature>.write-spec-questions.md`) instead of asking in chat. When the user signals the file is complete, validate, ingest answers into the spec (making the spec self-contained), then auto-archive per the same section.

Write the spec with sections:
- Summary
- Goals / Non-goals
- Requirements
- Acceptance Criteria
- Design (high-level)
- Edge cases
- Test Plan
- Rollout / Backout (if relevant)
- Open questions (resolved)

There should be no open questions or ambiguities left at the end of this process. If there are, then continue asking questions until they are resolved, providing your recommendations.

Append an entry to `workflow-docs/audit.md` with: timestamp, phase (`write-spec`), user request summary, assistant action summary, artifacts created/updated, decisions made, and next step.

Read `workflow-docs/workflow-state.md` at the start of this prompt and update it at the end: set Current Phase to `Write Spec`, set Active Artifact to the new spec path, refresh Current Feature, Current Objective, Next Immediate Action (`/write-plan`), Last Updated, Last Prompt Run, and tick the Write Spec / PRD checkbox.

At the end, tell me to run `/write-plan`.