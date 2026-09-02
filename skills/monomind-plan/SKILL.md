---
name: monomind-plan
description: "Break an approved spec, proposal, or large request into dependency-aware tracer-bullet tasks. Use when work needs ordered vertical slices, acceptance criteria, blocking edges, a ready frontier, a dependency graph, or safe distribution across sessions or agents. Do not invoke merely to restate a small obvious change."
---

# Monomind Plan

Produce an executable dependency graph whose ready tasks can be completed and verified independently.

## Plan from evidence

1. Read the source spec and inspect the affected code, tests, project instructions, domain vocabulary, and current work state. Planning is read-only unless the user also requested tracker or file updates.
2. Identify the behavior path, architectural seams, compatibility constraints, risks, and unknowns. Resolve facts through inspection; leave material decisions visibly open.
3. Draft **tracer bullets**: narrow, complete paths through the layers needed to deliver one observable behavior. Each task should fit a fresh focused context and leave the system in a valid state.
4. Put enabling refactors before the behavior they unlock. Prefer making the change easy, then making the easy change; do not smuggle unrelated cleanup into an enabling task.
5. Draw blocking edges from prerequisites to dependents. A task with no blockers belongs to the ready frontier. Remove cycles rather than scheduling around them.
6. Put high-uncertainty work early when its result can invalidate later tasks.

## Handle work that cannot slice vertically

A mechanical change with a wide blast radius may be safer as **expand–migrate–contract**:

1. Expand: add the new form beside the old while preserving compatibility.
2. Migrate: move consumers in independently verifiable batches.
3. Contract: remove the old form only after every consumer is proven migrated.

Use this exception for genuinely wide compatibility changes, not as a reason to organize ordinary feature work by technical layer.

## Task contract

Each task must state:

```markdown
## <Task title>

- Outcome: the observable behavior or enabling condition delivered
- Acceptance criteria: specific pass/fail statements
- Verification: focused checks plus any runtime evidence
- Blocked by: task names, or none
- Scope boundary: what this task deliberately does not include
- Risks or open decisions: only those local to this task
```

Use the task target already selected by the project. If none exists, propose a local plan location rather than mutating an external tracker. Never overwrite or bulk-close incomplete work from another effort. Creating or changing external issues requires authority for that tracker operation.

Before publishing, show the proposed granularity and dependency graph when a choice would materially affect sequencing, ownership, or cost.

## Completion criteria

- Every task delivers a behavior or named enabling condition and has acceptance criteria.
- Blocking edges form an acyclic graph; the ready frontier is identifiable.
- Normal feature tasks are vertical slices; wide refactors explain why they are exceptions.
- Each task is small enough for one focused context and leaves the repository verifiable.
- The plan has one canonical task target and does not duplicate or overwrite active work.
