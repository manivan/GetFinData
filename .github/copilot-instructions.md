# Copilot Instructions — [PROJECT NAME]

<!--
  TEMPLATE INSTRUCTIONS
  =====================
  This file is the primary Copilot context for your project.
  Replace each [FILL IN] section with your project-specific details.
  Delete these comment blocks once filled in.

  The "AI Workflow" section at the bottom applies to all projects — keep it as-is.
-->

## Project Overview

<!--
  [FILL IN]
  - What is this project? (1–2 sentences)
  - What is the tech stack?
  - What is the core pattern or user-facing flow?
-->

**[Project Name]** is a [brief description of what the project does and its tech stack].

The core pattern is:
1. [Describe the primary flow — e.g., "A user submits a form which triggers X"]
2. [Describe the secondary flow if applicable — e.g., "A background job processes X and updates Y"]

## Commands

<!--
  [FILL IN]
  List the key commands developers run day-to-day: test, lint, build, format, start, deploy, etc.
  Include any git hook automation (Husky, pre-commit, etc.).
-->

```bash
# Run tests
[your-test-command]

# Lint
[your-lint-command]

# Build
[your-build-command]

# Format
[your-format-command]
```

[Describe any git hook automation, e.g. "Husky runs prettier + eslint + tests on every `git commit`."]

## Architecture

<!--
  [FILL IN]
  Describe the high-level architecture. Include the sections most relevant to your project.
  Suggested sections: Data Flow, Key Modules/Components, Directory Structure, External Integrations.
-->

### Data Flow

```
[Describe how data moves through the system as a text diagram, e.g.:]
User → [Entry Point] → [Service/Logic Layer] → [Data Layer] → [Output/Response]
```

### Key Modules / Components

| Module / Component | Role |
|---|---|
| `[name]` | [what it does] |
| `[name]` | [what it does] |

### Directory Structure

```
[Describe key directories and what they contain, e.g.:]
src/         Application source code
tests/       Unit and integration tests
workflow-docs/  Workflow-generated specs and plans
tools/       Developer utilities (not deployed)
```

## Key Conventions

<!--
  [FILL IN]
  Document conventions Copilot must follow in this codebase.
  Examples: naming rules, error handling patterns, test file locations, injection patterns.
-->

### Naming Conventions
- [e.g., "Files use kebab-case; classes use PascalCase"]

### Testing
- [e.g., "Tests live in `__tests__/` alongside source files"]
- [e.g., "Use dependency injection / test statics for external calls — avoid real network/DB calls in unit tests"]

### Error Handling
- [e.g., "All exceptions are caught at the service boundary and return empty results, not thrown to the UI"]

### Style
- [e.g., "Keep functions small and focused; use type hints; prefer readable logging over clever one-liners"]

---

## AI Workflow

The following sections govern how Copilot works in this repository. Keep them as-is across all projects that use this template.

### Research & Exploration
- Always run deep research, codebase exploration, and spec/plan writing as background work via the `Explore` subagent (or another appropriate agent invoked through `runSubagent`)
- Never do deep exploration in the current context — delegate to a subagent
- Batch independent research questions into parallel subagent invocations

### Local Knowledge First

Before proposing or generating code that uses any library, API, or tool behavior:
1. If `docs/_knowledge/index.md` exists, read it to find the correct local doc file(s). If the folder does not exist, skip this rule — it is optional per the project's setup.
2. Read the referenced local knowledge files under `docs/_knowledge/**`.
3. If the required info is missing or ambiguous (and the folder exists), STOP and ask for:
   - Library/tool name and version (if relevant)
   - The exact behavior needed
   - Optionally: a snippet from official docs to pin locally
4. When using a fact from local docs, cite it by file path (e.g., `"See docs/_knowledge/js/express.md"`).

Hard rules:
- Do **not** invent APIs.
- If uncertain, ask questions or request a pinned note be added to `docs/_knowledge/` (if the folder exists).

### Live Codebase Verification

**Always verify facts against the live codebase before acting on them. Never rely on cached or remembered knowledge of the code.**

This applies to every prompt and every change — brainstorming, writing specs, writing plans, and executing slices. There is no pre-generated codebase summary to lean on; the source of truth is the code itself, as it exists right now.

Before proposing a path, function signature, module boundary, convention, dependency, or behavior:

1. Use `file_search`, `grep_search`, `semantic_search`, or `read_file` (or a background `Explore` subagent for non-trivial questions) to confirm the fact in the current code.
2. Cite the file path (and line range when useful) for any claim you make about the codebase.
3. If a fact cannot be confirmed, say so explicitly — do not infer or guess. Ask the user, or flag it as an open question.

When to use direct search vs. subagent:
- **Direct search tools** — single-fact verification (does this path exist? what is this function's signature? where is this symbol used?).
- **`Explore` subagent** — questions that require reading and synthesizing ~5+ files (how does this subsystem work? what are the conventions across these modules? where are all the places this pattern is used?).

Rules:
- Do NOT assume a file, module, or pattern still exists because it existed in an earlier session, a prior artifact, or a previous answer in this conversation.
- Do NOT trust a path mentioned in a spec, plan, or audit entry without re-confirming it exists.
- Prefer batched parallel reads over many small sequential reads when verifying multiple facts.
- For repeated structural questions within a single conversation, you may rely on facts you have just verified earlier in the **same** turn or recent turns — but re-verify at the start of any new SDLC phase prompt.

The cost of one extra search is far less than the cost of confidently citing a stale or non-existent path.

### Clarification Bias

**When in doubt, ask. Overconfidence leads to poor outcomes.**

- Default to asking a clarifying question whenever a requirement, scope, or constraint is ambiguous — do NOT proceed on an unstated assumption.
- Look for vague signals: "depends", "maybe", "not sure", "mix of", "somewhere between", "the right way", undefined nouns, references to external systems you have not been told about.
- Better to over-clarify than to implement the wrong thing. The cost of one extra question is far less than the cost of rework.
- For >~3 batched clarifications or anything gating a phase artifact, use a question file (see "Question Files" below). Single small clarifications stay in chat.

### Adaptive Depth

**Create exactly the detail needed for the problem at hand — no more, no less.**

The required artifacts for each phase are fixed (PRD, spec, plan, issues), but the **level of detail** inside them must scale to the problem.

Factors that drive detail level:
- Request clarity — how complete is the user's intent?
- Scope — single file, one component, multiple components, system-wide?
- Risk — what's the blast radius of getting it wrong?
- Brownfield vs. greenfield context.

Apply by example:
- **Simple bug fix** — terse spec, 2–3 acceptance criteria, no diagrams, one-slice plan.
- **System migration** — comprehensive PRD with functional + non-functional requirements, traceability, multi-phase plan with explicit risks.

Do not inflate simple problems with ceremony. Do not shortchange complex problems by omitting critical detail.

### Session Resumption

At the start of every conversation (and at the start of every SDLC phase prompt), read [workflow-docs/workflow-state.md](workflow-docs/workflow-state.md) first.

If the file shows an active feature, phase, or open question file, surface a brief "welcome back" summary before doing anything else:

- **Current Phase**: <phase>
- **Current Feature**: <feature>
- **Active Artifact**: <path or N/A>
- **Open Question Files**: <list or none>
- **Next Immediate Action**: <action>

Then confirm with the user before resuming: are we continuing the active work, or starting something new? Do not silently pick up the previous task — the user may have switched contexts.

If `workflow-state.md` does not exist yet, create it from the template fields documented in the file itself and treat the workspace as a fresh start.

### Content Validation

Before writing any file that contains embedded structured content (Mermaid diagrams, JSON, YAML, code fences), validate it parses:

**Mermaid**:
- Node IDs must be alphanumeric + underscores only. For labels with spaces or special characters, use `A[Display Label]` syntax (not bare `User Login`).
- Escape `"` and `'` inside labels.
- Verify arrow syntax (`-->`, `-->|label|`, `--text-->`) is consistent within the diagram.
- Mentally parse the diagram before writing. If validity is uncertain, replace it with a text-based representation (numbered list, ASCII outline, or table) rather than ship a broken diagram.

**JSON / YAML in code fences**:
- Verify brackets/braces are balanced and indentation is consistent.
- Escape quotes correctly.
- Do not output partial or "..."-truncated structures in artifacts that are meant to be referenced as specs.

**Fallback rule**: When in doubt about whether structured content will render, fall back to plain prose or a numbered list. A correct text description beats a broken diagram.

### Structured Reasoning Protocol

For complex tasks, follow this protocol (do not output private chain-of-thought):
1. **Goal** — 1–2 lines describing the objective
2. **Assumptions + unknowns** — bullet list
3. **Clarifying questions** — max 7 at a time, if needed before proceeding. If more than ~3 questions are needed, or the questions gate a phase artifact (PRD / spec / plan / issues), use a **question file** (see next section) instead of asking in chat.
4. **Plan with checkpoints** — bulleted, ordered steps
5. **Execute in slices** — edit → test → verify → summarize
6. **Final summary** — changed files, how to run tests, what's next

### Question Files

For multi-question clarifications that gate a phase artifact, write a **question file** to disk rather than asking in chat. Single small clarifications (≤3 questions, not blocking an artifact) and trivial fixes still use chat.

Conventions:
- Location: `workflow-docs/questions/<feature>.<phase>-questions.md` (e.g. `workflow-docs/questions/oauth.brainstorm-questions.md`).
- Format: multiple-choice with a mandatory `Other` option as the last choice, and an `[Answer]: ` tag per question. Minimum 2 meaningful options + `Other`.
- Frontmatter:

  ```yaml
  ---
  status: open       # open | answered | ingested | superseded
  feature: <name>
  phase: <brainstorm | write-spec | write-a-prd | write-plan | prd-to-plan | prd-to-issues>
  created: <YYYY-MM-DD HH:MM TZ>
  ingested_into: ""  # set on ingestion
  ingested_at: ""    # set on ingestion
  ---
  ```

- While the file is `open`, reference it from `workflow-docs/workflow-state.md` under "Blockers & Open Questions".
- Inform the user the file was created and wait for them to signal completion ("done" / "completed" / "finished").

Ingestion and auto-archive (AI performs all steps; no manual housekeeping):

When the user signals completion, the AI MUST:

1. Read the file and validate every `[Answer]:` tag is non-empty and uses a valid letter from the options. If any are missing or invalid, stop and prompt the user to complete them — do not partial-ingest.
2. Detect contradictions and ambiguities across answers. If any are found, create `workflow-docs/questions/<feature>.<phase>-clarification-questions.md` using the same format and stop; do not ingest until clarifications are answered. The original and clarification files are archived together once resolved.
3. Ingest the substance of every answer into the downstream artifact (PRD / spec / plan / issues). Downstream artifacts MUST be self-contained — the AI must not depend on re-reading the question file during later phases.
4. Update the question file frontmatter: `status: ingested`, `ingested_into: <artifact path>`, `ingested_at: <timestamp>`.
5. Move the file with `git mv` to `workflow-docs/questions/archive/<YYYY-MM-DD>-<original-name>.md`.
6. Append an audit entry to `workflow-docs/audit.md` recording: source path → archived path → downstream artifact.
7. Clear the file reference from `workflow-docs/workflow-state.md` "Blockers & Open Questions".

Steps 3–7 happen as one atomic ingestion. The AI MUST NOT archive a file that is still referenced as the active blocker without first clearing the blocker reference in the same operation.

Post-ingestion reference rules:
- Archived question files are reference-only.
- Consult an archived file ONLY to: trace a past decision, resolve a contradiction with a newly stated requirement, or support re-planning after scope change.
- If routine implementation work requires re-reading the archive, the ingestion was incomplete — fix the downstream artifact instead of leaning on the archive.

Garbage collection:
- Files left `open` for longer than ~30 days are flagged as stale in `workflow-state.md` under "Blockers & Open Questions".
- The AI MUST NOT auto-delete abandoned question files. Removal is a human action.

### Audit Logging

Maintain a project audit log at `workflow-docs/audit.md`.

Rules:
- Create `workflow-docs/audit.md` if it does not exist.
- Append an entry at the end of each SDLC phase prompt (`brainstorm`, `write-a-prd`, `write-spec`, `write-plan`, `prd-to-plan`, `prd-to-issues`) and after each executed slice in `execute-plan`.
- Keep entries concise and factual.
- Sanitize appended field values: replace `&` -> `&amp;`, `<` -> `&lt;`, and `>` -> `&gt;` before writing to `workflow-docs/audit.md`.

Each audit entry must include:
- Timestamp
- Prompt or phase name
- User request summary
- Assistant action summary
- Artifacts created/updated
- Decisions made
- Validation/test status (if applicable)
- Next step

### Workflow State

Maintain a live workflow state file at `workflow-docs/workflow-state.md`. This file is the single source of truth for **current phase** and **next immediate action**, readable by both humans and AI.

Rules:
- Create `workflow-docs/workflow-state.md` from the template if it does not exist.
- At the start of any SDLC prompt (`brainstorm`, `write-a-prd`, `write-spec`, `write-plan`, `prd-to-plan`, `prd-to-issues`, `execute-plan`), READ `workflow-docs/workflow-state.md` first to ground in current state.
- At the end of every SDLC prompt run, UPDATE `workflow-docs/workflow-state.md` to reflect the new state.
- During `execute-plan`, update the Execution Progress table after each slice.
- Keep the file concise — it holds only **active** state. All history and rationale go in `workflow-docs/audit.md`.
- Never delete prior audit entries when updating state; the two files have different lifecycles.

Each state update must refresh:
- Current Phase
- Current Feature
- Active Artifact
- Last Updated timestamp
- Last Prompt Run
- Current Objective
- Next Immediate Action
- Phase Checklist (tick completed phases)
- Execution Progress table (during `execute-plan`)
- Blockers & Open Questions

### SDLC Phases

This project follows a four-phase AI-assisted development workflow. Use the prompt files in `.github/prompts/` to drive each phase:

| Phase | Prompt | Output Artifact |
|---|---|---|
| 1. Brainstorm | `brainstorm` | Design decisions resolved, shared understanding + audit entry |
| 2. Write Spec | `write-a-prd` or `write-spec` | `workflow-docs/specs/<feature>.prd.md` or `workflow-docs/specs/<feature>.spec.md` + audit entry |
| 3. Write Plan | `write-plan` or `prd-to-plan` | `workflow-docs/plans/<feature>.plan.md` + audit entry |
| 4. Execute | `execute-plan` | Implemented code + passing tests + per-slice audit entries |

Supporting prompts: `debug`, `tdd`, `request-refactor-plan`, `improve-codebase-architecture`, `prd-to-issues`.

### Vertical Slice Suitability

Vertical slicing (tracer bullets) is the **default and preferred** approach for plans and issues. Before producing a plan or issues, verify the work is suitable for vertical slicing by checking:

1. Is there user-visible behavior to deliver?
2. Can a thin path through all layers be demoed end-to-end?
3. Is each candidate slice independently shippable?

If any answer is "no," STOP and recommend an alternative approach before proceeding:

- **Pure infrastructure / migration** → phased migration plan (strangler fig, dual-write, cutover)
- **Foundational platform work** → spike + ADR, then a thin first consumer
- **Cross-cutting non-functional work** → checklist-driven rollout per service/module
- **Research spike** → time-boxed spike with a written conclusion, no merge
- **Refactor with no behavior change** → use `/request-refactor-plan`
- **Single-layer fix / trivial change** → skip planning, single PR

Do not silently switch approaches. Present the suitability finding and proposed alternative, and let the user confirm or override ("force vertical anyway").
