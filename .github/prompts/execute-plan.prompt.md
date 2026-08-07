---
name: execute-plan
description: Execute the plan, implement changes, and run tests.
model: claude-sonnet-4.6
---

Plan path:
${input:plan:workflow-docs/plans/<feature>.plan.md}

Rules:
- Read `workflow-docs/workflow-state.md` first to identify the active plan and next pending slice
- Execute in small slices
- After each slice, run the project's test command (check `docs/_knowledge/**` or `.github/copilot-instructions.md` for the correct command)
- For each slice, create a local branch using: `feat/<local-id>-<short-slug>`
- Use commit messages prefixed by the local ticket ID: `<local-id>: <summary>`
- Merge each completed slice branch into local `main` only after tests pass
- After each completed slice:
  - Append an entry to `workflow-docs/audit.md` with: timestamp, phase (`execute-plan`), local ticket ID, branch, summary of changes, test status, and next step
  - Update `workflow-docs/workflow-state.md`: set the slice row status to `done` (or `in-progress`/`blocked` as appropriate), refresh Current Objective, Next Immediate Action (next pending slice), Last Updated, Last Prompt Run; when all slices are done, set Current Phase to `Idle` and tick the Execute checkbox
- If any library usage is uncertain, consult `docs/_knowledge/**` first
- Summarize: changed files + test results + next steps