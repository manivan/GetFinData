---
name: improve-codebase-architecture
description: Explore a codebase to find opportunities for architectural improvement, focusing on making the codebase more testable by deepening shallow modules. Use when user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, and make a codebase more AI-navigable.
model: claude-opus-4.6
---


# Variables
- REFERENCE_FILE: improve-codebase-architecture-REFERENCE.md

# Improve Codebase Architecture

Explore a codebase like an AI would, surface architectural friction, discover opportunities for improving testability, and propose module-deepening refactors as local markdown RFCs.

A **deep module** (John Ousterhout, "A Philosophy of Software Design") has a small interface hiding a large implementation. Deep modules are more testable, more AI-navigable, and let you test at the boundary instead of inside.

## Process

### 1. Explore the codebase

Use the Agent tool with subagent_type=Explore to navigate the codebase naturally. Do NOT follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small files?
- Where are modules so shallow that the interface is nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called?
- Where do tightly-coupled modules create integration risk in the seams between them?
- Which parts of the codebase are untested, or hard to test?

The friction you encounter IS the signal.

Be sure to check existing git worktrees to see what rearchitecture is already happening and avoid proposing work that's already in progress.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate, show:

- **Cluster**: Which modules/concepts are involved
- **Why they're coupled**: Shared types, call patterns, co-ownership of a concept
- **Dependency category**: See **REFERENCE_FILE** for the four categories
- **Test impact**: What existing tests would be replaced by boundary tests

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. User picks a candidate

### 4. Frame the problem space

Before spawning sub-agents, write a user-facing explanation of the problem space for the chosen candidate:

- The constraints any new interface would need to satisfy
- The dependencies it would need to rely on
- A rough illustrative code sketch to make the constraints concrete — this is not a proposal, just a way to ground the constraints

Show this to the user, then immediately proceed to Step 5. The user reads and thinks about the problem while the sub-agents work in parallel.

### 5. Design multiple interfaces

Spawn 3+ sub-agents in parallel using the Agent tool. Each must produce a **radically different** interface for the deepened module.

Prompt each sub-agent with a separate technical brief (file paths, coupling details, dependency category, what's being hidden). This brief is independent of the user-facing explanation in Step 4. Give each agent a different design constraint:

- Agent 1: "Minimize the interface — aim for 1-3 entry points max"
- Agent 2: "Maximize flexibility — support many use cases and extension"
- Agent 3: "Optimize for the most common caller — make the default case trivial"
- Agent 4 (if applicable): "Design around the ports & adapters pattern for cross-boundary dependencies"

Each sub-agent outputs:

1. Interface signature (types, methods, params)
2. Usage example showing how callers use it
3. What complexity it hides internally
4. Dependency strategy (how deps are handled — see **REFERENCE_FILE**)
5. Trade-offs

Present designs sequentially, then compare them in prose.

After comparing, give your own recommendation: which design you think is strongest and why. If elements from different designs would combine well, propose a hybrid. Be opinionated — the user wants a strong read, not just a menu.

### 6. User picks an interface (or accepts recommendation)

### 7. Create local RFC

Create a refactor RFC as a local markdown file at `workflow-docs/specs/<feature>.architecture-rfc.md`. Use the template in **REFERENCE_FILE**. If `workflow-docs/specs/` does not exist, create it. Do NOT ask the user to review before creating — just create it and share the local file path.

### 8. Append an audit entry

Append an entry to `workflow-docs/audit.md` with: timestamp, phase (`improve-codebase-architecture`), user request summary, assistant action summary, artifacts created/updated (the RFC path), candidate chosen, interface design chosen, and next step.

### 9. Update workflow state

Read `workflow-docs/workflow-state.md` at the start of this prompt and update it at the end: set Active Artifact to the new RFC path, refresh Current Feature, Current Objective, Next Immediate Action (typically `/request-refactor-plan` to convert the RFC into commit-by-commit steps, or `/execute-plan` if the RFC is already actionable), Last Updated, and Last Prompt Run. Do NOT tick any of the per-feature Phase Checklist boxes — this prompt produces an architecture RFC, not a feature artifact.
