# AI-Assisted SDLC Template

A GitHub Copilot configuration template that brings a structured, workflow-driven development process to any project.

> **Important:** This workflow is designed to work only with GitHub Copilot.

## Table of Contents

- [What This Is](#what-this-is)
- [Quick Start](#quick-start)
- [SDLC Workflow](#sdlc-workflow)
- [Workflow Options](#workflow-options)
- [Maintenance Prompts](#maintenance-prompts)
- [Running Prompts](#running-prompts)
- [File Structure](#file-structure)
- [Audit Logging](#audit-logging)
- [Workflow State](#workflow-state)
- [Question Files](#question-files)
- [GitHub CLI Examples](#github-cli-examples)

---

## What This Is

This repository is a **drop-in template** — copy its `.github/` folder into any project to give GitHub Copilot:

- **Project context** — a structured place to describe your architecture, commands, and conventions
- **A four-phase SDLC workflow** — Brainstorm → Spec → Plan → Execute
- **Reusable prompt library** — named slash-command prompts for every phase of development
- **AI behavior rules** — live codebase verification, local-knowledge-first, clarification bias, structured reasoning, subagent delegation

> **How it works:** GitHub Copilot automatically reads `.github/copilot-instructions.md` as background context for every conversation. The `.github/prompts/` folder makes each prompt available as a `/slash-command` in VS Code Copilot Chat.

---

## Quick Start

### 1. Copy the template into your project

Clone this repo (if you haven't already), then copy the `.github/` folder into your project root:

```bash
git clone <this-repo-url>
cp -r workflow-driven-dlc-copilot-template/.github /path/to/your-project/
```

### 2. Fill in your project context

Open `.github/copilot-instructions.md` and replace every `[FILL IN]` placeholder with details about your project:

- **Project Overview** — what the project is, the tech stack, and the core user-facing pattern
- **Commands** — the exact commands to run tests, lint, build, and format
- **Architecture** — how data flows through the system, key modules, and directory structure
- **Key Conventions** — naming rules, testing patterns, error handling, and style decisions

> The **AI Workflow** section at the bottom of the file governs all Copilot behavior in this repo (Research & Exploration, Local Knowledge First, Live Codebase Verification, Clarification Bias, Adaptive Depth, Session Resumption, Content Validation, Structured Reasoning, Question Files, Audit Logging, Workflow State, SDLC Phases, Vertical Slice Suitability) — keep it as-is.

### 3. Clean up

Delete the `<!-- ... -->` comment blocks once you've filled everything in.

### 4. (Optional but recommended) Set up the local knowledge base

Create a `docs/_knowledge/` folder in your project and pin notes for any libraries or APIs you use. Copilot checks this folder before writing any code — this prevents hallucinated APIs.

```
docs/
  _knowledge/
    index.md          # Maps each topic to its file (e.g., "express → js/express.md")
    js/
      express.md      # Pinned notes about Express.js behavior and APIs
    [language]/
      [topic].md
```

### 5. Start using the workflow

Open VS Code with GitHub Copilot Chat. For your first feature, start with:

```
/brainstorm
```

---

## SDLC Workflow

The workflow follows four phases for building new features. Each phase has a dedicated prompt. Use them in order, or jump to any phase as needed.

```
1. Brainstorm        →  Resolve design decisions and ambiguities
2. Write PRD         →  workflow-docs/specs/<feature>.prd.md
3. Write Plan        →  workflow-docs/plans/<feature>.plan.md
4. Execute           →  Code + tests, slice by slice
```

For traceability, append an audit entry to `workflow-docs/audit.md` after each phase and after each executed ticket.

> **About "tracer-bullet" slices:** Phases 3 and 4 break work into *vertical slices* — each slice cuts through every layer of the stack (schema, API, UI, tests) end-to-end and is independently demoable. This is the opposite of "do all the database work first, then the API, then the UI."

> **About Phase 2b / 3b:** These are lightweight alternatives to Phases 2 and 3 for cases where you already know what you want — they skip the interview and go straight to writing.

### Phase 1 — Brainstorm

**Goal:** Resolve all design decisions and ambiguities before writing anything down.

Copilot interviews you relentlessly about your plan — walking down every branch of the decision tree until there are no open questions.

```
/brainstorm
```

**Example triggers:**
```
"Brainstorm my plan for adding OAuth login"
"Grill me on this architecture"
"I want to stress-test my design for the notification system"
```

**Output:** Shared understanding — no artifacts written to disk yet.

Also append an entry to `workflow-docs/audit.md` summarizing decisions and next steps.

---

### Phase 2 — Write PRD (Product Requirements Document)

**Goal:** Capture the resolved decisions from the brainstorm into a structured requirements document.

Copilot explores the codebase, sketches the major modules to build or modify, and writes a PRD. The PRD includes: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, and Out of Scope.

```
/write-a-prd
```

**Example triggers:**
```
"Write a PRD for the feature we just discussed"
"Create a product requirements document for OAuth login"
"Turn this brainstorm into a PRD"
```

**Output:** `workflow-docs/specs/<feature>.prd.md`

Also append an entry to `workflow-docs/audit.md` summarizing scope, decisions, and created artifacts.

> **Tip:** Run `/write-a-prd` immediately after `/brainstorm` in the same conversation — it will use the resolved decisions already in context without re-interviewing you.

---

### Phase 2b — Write Spec *(lightweight alternative to Phase 2)*

**Goal:** Write a concise spec when the design is already clear and you don't need a full interview.

Copilot consults the local knowledge base, asks any remaining clarifying questions, and writes the spec. At the end it prompts you to run `/write-plan`.

```
/write-spec
```

**Example triggers:**
```
"Write a spec for the password reset feature"
"I know what I want to build — write a spec for it"
"Create a spec doc for the CSV export endpoint"
```

**Output:** `workflow-docs/specs/<feature>.spec.md` (Summary, Goals/Non-goals, Requirements, Acceptance Criteria, Design, Edge Cases, Test Plan)

Also append an entry to `workflow-docs/audit.md` summarizing resolved questions, key decisions, and next steps.

---

### Phase 3 — Write Plan

**Goal:** Break the PRD into a phased implementation plan using tracer-bullet vertical slices.

Each slice cuts end-to-end through all layers and is independently demoable. Copilot quizzes you on the proposed breakdown before writing the plan file.

```
/prd-to-plan
```

**Example triggers:**
```
"Break this PRD into a plan"
"Create an implementation plan for the OAuth PRD"
"Turn workflow-docs/specs/oauth.prd.md into tracer bullet phases"
```

**Output:** `workflow-docs/plans/<feature>.plan.md`

Also append an entry to `workflow-docs/audit.md` summarizing phase breakdown and major risks.

> **Tip:** For simpler features with a spec (not a full PRD), use `/write-plan` instead — it converts a spec directly into an ordered plan with checkpoints and risk mitigations.

---

### Phase 3b — Create Issues *(optional alternative to Phase 3)*

**Goal:** Break the PRD into independently-grabbable local tickets instead of (or alongside) a plan.

Each ticket is a vertical slice with its own acceptance criteria, dependencies, and user stories. Tickets are saved locally — no GitHub required.

```
/prd-to-issues
```

**Example triggers:**
```
"Break this PRD into tickets"
"Create a local issue backlog for the OAuth feature"
"Give me independently-grabbable work items from this PRD"
```

**Output:** `workflow-docs/specs/<feature>.issues.md` with tickets formatted as `AUTH-001`, `AUTH-002`, etc.

Also append an entry to `workflow-docs/audit.md` summarizing created ticket IDs and dependencies.

---

### Phase 4 — Execute

**Goal:** Implement the plan slice by slice, running tests after each slice.

Copilot creates a local git branch per slice, implements the code, runs the project's test command, and merges into `main` only when tests pass.

```
/execute-plan
```

**Example triggers:**
```
"Execute the plan at workflow-docs/plans/oauth.plan.md"
"Implement phase 1 of the OAuth plan"
"Start building from the plan"
```

**Output:** Implemented code committed to local git branches, merged into `main` after tests pass.

Also append an entry to `workflow-docs/audit.md` after each executed slice with ticket ID, branch, tests, and next step.

> **Tip:** You can run `/execute-plan` one phase at a time to review progress between slices, or let it run the full plan autonomously.

---

## Workflow Options

Choose your workflow based on uncertainty, team size, and the level of traceability you need.

**Core decision rule**

- Use more phases when requirements are ambiguous or work is high-risk and multi-person.
- Use fewer phases when scope is clear and you need speed.

### Option 1: Brainstorm -> PRD -> Plan -> Execute

Default path for medium and large features.

**Pros**

- Strong decisions up front.
- PRD captures user value and scope boundaries clearly.
- Plan converts requirements into executable slices.
- Lower risk of building the wrong thing.

**Cons**

- More upfront effort.
- Can feel heavy for small fixes.
- Requires discipline to keep PRD and plan aligned.

**Best use cases**

- New features with unknowns.
- Features touching multiple modules.
- Work where you want clear "why" and "what" before coding.

### Option 2: Brainstorm -> Spec -> Plan -> Execute

Lighter than the PRD path, while still structured.

**Pros**

- Faster than the full PRD flow.
- Retains acceptance criteria and design clarity.
- Good balance of speed and rigor.

**Cons**

- Less product-level narrative than a PRD.
- Can miss broader scope tradeoffs on complex efforts.

**Best use cases**

- Internal or developer-facing features.
- Small-to-medium features that are mostly understood.
- Solo or small-team delivery where speed matters.

### Option 3: PRD -> Plan -> Execute

Skip brainstorm when requirements are already stable and aligned.

**Pros**

- Efficient when the PRD is already high quality.
- Keeps a strong requirements artifact.
- Good traceability.

**Cons**

- Hidden ambiguities can survive if the PRD is weak.
- Less challenge-testing of assumptions.

**Best use cases**

- You already ran discovery elsewhere.
- Requirement source is trusted and aligned.
- Incremental features with known patterns.

### Option 4: Spec -> Plan -> Execute

Fastest path that still preserves structure.

**Pros**

- Minimal overhead.
- Quick handoff to implementation.
- Still maintains acceptance criteria.

**Cons**

- Easier to under-spec edge cases.
- Weaker long-term product history than the PRD-based path.

**Best use cases**

- Bug fixes and small enhancements.
- Time-sensitive work.
- Clear, constrained technical tasks.

### Option 5: PRD (or Spec) -> Plan -> Issues -> Execute

Adds explicit ticketization before implementation.

**Pros**

- Best for parallel execution.
- Clear dependencies and blockers.
- Cleaner branch, commit, and ownership discipline.
- Better progress tracking and handoff.

**Cons**

- More overhead and maintenance.
- Can over-fragment small features.

**Best use cases**

- Multi-developer work.
- Asynchronous collaboration.
- Need for predictable delivery tracking.

### Option 6: Brainstorm -> PRD -> Plan -> Issues -> Execute

Most rigorous end-to-end flow.

**Pros**

- Maximum clarity, traceability, and execution control.
- Strong fit for complex or risky initiatives.
- Great audit trail from intent to shipped slices.

**Cons**

- Highest process cost.
- Too heavy for small tasks.

**Best use cases**

- High-risk, high-impact features.
- Cross-cutting architecture work.
- Work requiring approvals or formal checkpoints.

### Practical Recommendation Matrix

| Situation | Recommended flow |
|---|---|
| Small bug or fix | Spec -> Plan -> Execute |
| Medium feature (some uncertainty) | Brainstorm -> Spec -> Plan -> Execute |
| Medium/large feature (product impact) | Brainstorm -> PRD -> Plan -> Execute |
| Team parallelization needed | Add Issues before Execute |
| High-risk or cross-team project | Brainstorm -> PRD -> Plan -> Issues -> Execute |

---

## Maintenance Prompts

These prompts operate independently of the SDLC flow. Use them reactively — for bugs, tech debt, and code quality work on existing code.

---

### Debug

**Goal:** Find the root cause of a bug by recursively asking "why" until reaching the fundamental issue.

Copilot explores the codebase like a detective — following every clue, checking git worktrees for in-progress work, and presenting a full root-cause chain with evidence and next steps.

```
/debug
```

**Example triggers:**
```
"Debug why the login flow returns a 401 intermittently"
"Find the root cause of this crash"
"RCA: payments are failing for users in the EU"
"Why is the export feature producing empty files?"
```

**Output:** Root-cause chain (why → why → why), evidence at each step, and actionable next steps.

---

### TDD

**Goal:** Build a feature or fix a bug test-first using the red-green-refactor loop.

Copilot works in vertical slices — one test → minimal implementation → repeat. Tests verify behavior through public interfaces only, so they survive internal refactors.

```
/tdd
```

**Example triggers:**
```
"Fix this bug using TDD"
"Build the password reset flow test-first"
"Red-green-refactor the cart checkout logic"
"Write integration tests for the user service"
```

**Output:** Tests + implementation committed in small, verified cycles.

> **Tip:** Use `/tdd` inside `/execute-plan` for individual slices, or standalone whenever you want test-first discipline on a focused change.

---

### Request Refactor Plan

**Goal:** Plan a safe, incremental refactor of existing code with tiny commits — each leaving the codebase in a working state.

Copilot interviews you about the problem, checks test coverage, explores the codebase to verify your assertions, and writes a refactor RFC.

```
/request-refactor-plan
```

**Example triggers:**
```
"Plan a refactor of the auth module"
"I want to extract the payment logic into its own service — help me plan it"
"Create a refactoring RFC for the database access layer"
"Break down this refactor into safe incremental steps"
```

**Output:** `workflow-docs/specs/<feature>.refactor.md` — a refactor RFC with problem statement, commit-by-commit plan, decisions, testing approach, and out-of-scope boundaries.

---

### Improve Codebase Architecture

**Goal:** Audit the codebase for architectural friction and surface opportunities to create deep modules — small interfaces hiding large implementations — making the code more testable and AI-navigable.

Copilot explores organically, presents refactor candidates, designs multiple interface options in parallel, gives a recommendation, and writes an architecture RFC.

```
/improve-codebase-architecture
```

**Example triggers:**
```
"Audit this codebase for architectural improvements"
"Find shallow modules I should deepen"
"Make this codebase more testable"
"Where is there too much coupling in this project?"
```

**Output:** `workflow-docs/specs/<feature>.architecture-rfc.md` — an architecture RFC with candidate analysis, interface design options, and a recommended approach.

---

## Running Prompts

Prompts are used in **VS Code with GitHub Copilot Chat**. There are two ways to invoke them:

**1. Slash command** — type the prompt name prefixed with `/`:
```
/brainstorm
/write-a-prd
/execute-plan
```

**2. Natural language** — each prompt auto-suggests based on what you type:
```
"Brainstorm my plan for the new auth system"
"Grill me on this design"
"Write a PRD for the export feature"
"Debug why the login flow is broken"
```

> **Note:** Prompt files require VS Code with GitHub Copilot Chat. The `model:` frontmatter in each prompt requires Copilot to support model selection (available in recent versions).

---

## File Structure

Only the `.github/` folder is part of this template — copy it into your project. Everything else (`workflow-docs/`, `README.md`) stays in this template repo.

```
.github/
  copilot-instructions.md   # Primary Copilot context — fill this in for your project
  prompts/
    # SDLC prompts
    brainstorm.prompt.md                     # Phase 1 — stress-test a design via interview
    write-a-prd.prompt.md                    # Phase 2 — create a PRD
    write-spec.prompt.md                     # Phase 2b — write a lightweight spec
    write-plan.prompt.md                     # Phase 3 (alt) — spec → implementation plan
    prd-to-plan.prompt.md                    # Phase 3 — PRD → phased plan
    prd-to-issues.prompt.md                  # Phase 3b — PRD → local tickets
    execute-plan.prompt.md                   # Phase 4 — implement slice-by-slice
    # Maintenance prompts
    debug.prompt.md                          # Root-cause analysis via recursive "why"
    tdd.prompt.md                            # Red-green-refactor TDD loop
    request-refactor-plan.prompt.md          # Interview-driven refactor RFC
    improve-codebase-architecture.prompt.md  # Find deep-module refactor opportunities
    # Reference files (used by prompts as context — not runnable directly)
    tdd-tests.md                             # Good vs bad test examples
    tdd-mocking.md                           # When and how to mock
    tdd-refactoring.md                       # Refactor candidates after TDD
    tdd-deep-modules.md                      # Deep module design reference
    improve-codebase-architecture-REFERENCE.md  # Dependency categories for architecture RFC
```

**Your project's `workflow-docs/` folder** is used by the workflow to store generated artifacts:

```
workflow-docs/
  audit.md                   # Append-only workflow log (phase outcomes, decisions, tests, next steps)
  workflow-state.md          # Live state: current phase, active artifact, next immediate action
  specs/
    <feature>.prd.md          # Created by /write-a-prd
    <feature>.spec.md         # Created by /write-spec
    <feature>.issues.md       # Created by /prd-to-issues
    <feature>.refactor.md     # Created by /request-refactor-plan
    <feature>.architecture-rfc.md  # Created by /improve-codebase-architecture
  plans/
    <feature>.plan.md         # Created by /prd-to-plan or /write-plan
  questions/
    <feature>.<phase>-questions.md  # Open question files awaiting human answers
    archive/
      YYYY-MM-DD-<feature>.<phase>-questions.md  # Auto-archived after ingestion
```

## Audit Logging

Use `workflow-docs/audit.md` as an append-only activity log across the workflow.

Append an entry:

- At the end of each SDLC prompt (`/brainstorm`, `/write-a-prd`, `/write-spec`, `/write-plan`, `/prd-to-plan`, `/prd-to-issues`)
- After each executed ticket or slice during `/execute-plan`
- At the end of `/request-refactor-plan` and `/improve-codebase-architecture` (both produce persistent RFCs)

Include these fields in each entry:

- Timestamp
- Prompt or phase name
- User request summary
- Assistant action summary
- Artifacts created/updated
- Decisions made
- Test status (if applicable)
- Next step

## Workflow State

Use `workflow-docs/workflow-state.md` as the live, single source of truth for **where the workflow is now** and **what to do next**. Both humans and AI agents read this file at the start of each prompt and update it at the end.

Key principles:

- Holds **active** state only — current phase, current feature, active artifact, next immediate action, phase checklist, execution progress.
- All history and rationale stays in `workflow-docs/audit.md`.
- Every SDLC prompt (`/brainstorm`, `/write-a-prd`, `/write-spec`, `/write-plan`, `/prd-to-plan`, `/prd-to-issues`, `/execute-plan`) reads it first and updates it last.
- The RFC-producing maintenance prompts (`/request-refactor-plan`, `/improve-codebase-architecture`) also read and update it, but do NOT tick per-feature Phase Checklist boxes — they refresh the Active Artifact and Next Immediate Action only.
- During `/execute-plan`, the Execution Progress table is updated after every slice.

## Question Files

For multi-question clarifications that gate a phase artifact (PRD, spec, plan, issues), the AI writes a **question file** to `workflow-docs/questions/` rather than asking in chat. This gives every Q&A an auditable, resumable, reviewable artifact.

When the AI uses a question file:

- More than ~3 clarifying questions are needed
- Questions gate a phase artifact (brainstorm output, PRD, spec, plan, issues)
- Contradictions or ambiguities are detected in earlier answers

When the AI uses chat instead:

- A single small clarification (≤3 questions) that does not block an artifact
- Trivial fixes or single-layer changes

File format:

- Multiple-choice with mandatory `Other` last option, `[Answer]: ` tag per question, YAML frontmatter (`status`, `feature`, `phase`, `created`, `ingested_into`, `ingested_at`).
- See the "Question Files" section in `.github/copilot-instructions.md` for the exact spec.

Lifecycle (AI-driven, no manual housekeeping):

1. AI creates `workflow-docs/questions/<feature>.<phase>-questions.md` and references it from `workflow-state.md` "Active Question Files".
2. Human fills in `[Answer]:` tags and signals "done".
3. AI validates answers, detects contradictions (creating a clarification file if needed), ingests substance into the downstream artifact, sets frontmatter to `status: ingested`, and `git mv`s the file to `workflow-docs/questions/archive/YYYY-MM-DD-<original-name>.md`.
4. AI logs the ingestion in `audit.md` and clears the open-file reference from `workflow-state.md`.

Important: archived question files are reference-only — used for tracing decisions, resolving new contradictions, or re-planning. Downstream artifacts are self-contained; the AI does not depend on archived files for routine work.

Abandoned files (left `open` >30 days) are flagged as stale in `workflow-state.md`. Only humans delete them.

**Your project's `docs/_knowledge/` folder** remains the local knowledge base used for pinned library/API notes:

```
docs/
  _knowledge/
    index.md                  # Your pinned library/API notes (manual)
    [language]/[topic].md
```

---

## GitHub CLI Examples

Use these templates to run workflow prompts from GitHub CLI in a consistent, repeatable sequence.

### Step 1: write-a-prd

```text
Please follow the workflow in write-a-prd.prompt.md.
Do not call skill(write-a-prd). Read that file and execute its process directly.
Output must be a local Markdown PRD at workflow-docs/specs/corrective-work-request.prd.md.

Context:
I am building a new Salesforce LWC form for a Corrective Work Request to create an N1 record.
This form runs online only.
When the user clicks Submit, data is sent to Salesforce and an N1 record is created.
Purpose: to allow users to report identified issues and generate N1 notification data.
[more information...]
```

### Step 2: prd-to-plan

```text
Please follow prd-to-plan.prompt.md.
Read corrective-work-request.prd.md.
Create a tracer-bullet vertical-slice plan and save it to workflow-docs/plans/corrective-work-request.plan.md.
Keep slices thin, demoable, and end-to-end.
```

### Step 3: prd-to-issues

```text
Read corrective-work-request.prd.md and corrective-work-request.plan.md.
Create local implementation tickets in workflow-docs/specs/corrective-work-request.issues.md.
Use IDs CWR-001, CWR-002, CWR-003, CWR-004, CWR-005, CWR-006.
For each ticket, include: title, status, blocked by, covered user stories, and acceptance criteria.
```

### Step 4: execute-plan

```text
Please follow execute-plan.prompt.md.
Implement only ticket CWR-001 from workflow-docs/specs/corrective-work-request.issues.md and the matching phase from workflow-docs/plans/corrective-work-request.plan.md.
Use branch feat/CWR-001-component-skeleton.
Run the relevant tests and summarize changed files, test results, and the next recommended ticket.
```

Before running Step 4, create the slice branch:

```bash
git checkout -b feat/CWR-001-component-skeleton
```

Execution notes:

- Test the output for each branch and ticket before moving to the next one.
- Ensure each ticket delivers an end-to-end increment that is both demoable and deployable.
- Do not move to the next ticket until the current one is validated in a runnable state.
- Append an entry to `workflow-docs/audit.md` after each step/ticket with summary, artifacts, test status, and next step.
- Repeat this process for CWR-001 through CWR-006 until all tickets are completed.