# Project workflow adoption

Read this reference only when adopting the Monomind workflow into a repository.
The portable skill cannot know project commands, shared resources, or authority
defaults, so adoption creates a small repository profile and a mandatory
instruction pointer.

## What installation does not do

Copying a skill folder only makes its name and description discoverable. The
body remains lazy until the agent selects the skill. Do not claim that a
repository follows Monomind merely because `.agents/skills/monomind-workflow`
exists.

Adoption adds the other two pieces:

- a managed block in the active root `AGENTS.md` or `AGENTS.override.md`, which
  requires the workflow before new code-changing tasks; and
- `.monomind/workflow.md`, which records verified project facts.

The bundled `scripts/adopt.py` performs the deterministic merge and drift check.
It copies `assets/workflow-profile.md` only when the target profile is absent.

## Evidence to inspect

Before filling the profile, inspect only sources relevant to these fields:

- remotes, default branch, branch naming, and integration strategy;
- manifests, task runners, checked-in CI, tests, linters, type checks, builds,
  and smoke-test configuration;
- architecture and dependency rules, migrations, generated files, security,
  reliability, and performance constraints;
- gitignored artifact paths, approved test data, visual targets, viewports, and
  capture restrictions;
- ports, databases, queues, caches, emulators, test accounts, and how a running
  service is tied to the task worktree; and
- change-request requirements, required reviewers, blocking gates, merge
  authority, and all other external-action boundaries.

Point to an existing authoritative source instead of copying a large instruction
set into the profile. Never invent a familiar command or permission for an empty
field. `UNRESOLVED` is an acceptable and visible result.

## Adoption checks

- The current task is a linked worktree on a named non-`main` branch based on
  the locally available `origin/main`.
- The workflow skill is project-local, so teammates receive the same version.
- Existing instruction text and an existing profile are preserved.
- The managed policy requires Isolate before editing, states the why/when versus
  reusable-how boundary, and routes visible UI work to matched proof.
- Every recorded command comes from checked-in configuration or a verified
  help/dry-run path.
- Local editing, commits, pushes, review replies, and merge authority are stated
  separately.
- `scripts/adopt.py check --repo <repository>` passes; unresolved profile values
  are reported rather than hidden.
- The handoff says that a new agent run is required before the newly written
  repository instructions become startup context.
