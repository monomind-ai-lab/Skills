# Monomind repository policy principles

Use these principles to frame the onboarding interview. They define the
factory's safety posture; the repository profile supplies the project-specific
people, commands, locations, gates, and exceptions needed to apply it.

## `UNRESOLVED` means stop and decide

- `UNRESOLVED` is an onboarding state, never an operational default.
- Agents discover mechanical facts and surface options. A repository owner,
  project lead, or explicitly named delegate defines and approves policy.
- An unknown cannot be turned into `NOT_APPLICABLE` merely because no config was
  found. Record `NOT_APPLICABLE — <reason>` only with evidence or approval.
- Preserve who approved a decision, when, and where its rationale lives. Review
  the profile when ownership, tooling, CI, release topology, or risk changes.

## Collaboration

- Give each task one named owner, one owned branch, and one owned worktree.
- Start implementation in a task-owned linked worktree from the approved
  authoritative base; reuse it across phases. Never edit on `main`, the
  configured base branch, or another task's workspace.
- Coordinate likely file overlap and shared resources before parallel work
  diverges. Worktrees do not isolate ports, databases, queues, caches, buckets,
  emulators, test accounts, or externally generated locks.
- Never stash, reset, rebase, overwrite, or delete another owner's unknown work.
- Record who reviews, who resolves conflicting requirements, where blockers are
  escalated, and who may clean up task state.

## Integration

- Integrate through the repository's configured change-request path; protect
  the authoritative base from direct implementation and direct push.
- Define one integration strategy—merge, squash, rebase, or another explicit
  method—and state who performs it. Do not infer strategy from personal habit.
- Reconcile the owned branch with the authoritative base before integration and
  rerun affected checks. Do not rewrite shared or protected history.
- Treat commit, push, change-request creation, review replies, and merge as
  separate authority gates.

## Testing

- Record exact repository-native setup and focused, regression, type/compile,
  lint/format, build/package, and runtime/smoke commands, including explicit
  not-applicable reasons.
- Prove changed behavior through a public seam. Obtain a failing signal first
  for a behavior change or regression when feasible, then run affected gates
  after the final relevant edit.
- Do not weaken, skip, or rewrite a check merely to make a change pass. State
  untested claims and reasons plainly.
- Bind runtime and visual evidence to the exact revision, environment, data
  class, and reproduction sequence.

## CI/CD

- Make required CI gates, triggers, reviewers, blocking-finding rules, retry
  authority, and override authority explicit. A green optional job is not a
  substitute for the declared required gate set.
- Keep policy in reviewed repository configuration where possible and enforce
  server-side invariants with branch protection or equivalent controls.
- CI verifies a revision; it does not retroactively make unsafe local editing or
  unauthorized publication acceptable.
- Any bypass or override needs a named decision maker, rationale, evidence, and
  follow-up condition.

## Release

- Separate readiness assessment, release preparation, and live execution.
  Deployment, migration, traffic changes, and notification each require exact
  authority for the target environment.
- Identify the artifact, environments, promotion path, release owner, approver,
  success/failure signals, observation window, and rollback decision maker.
- Prefer compatibility-preserving and staged changes when project risk warrants
  them. Database changes should make rollback and mixed-version operation
  credible rather than assumed.
- Record what shipped, the checks and approvals, observed signals, decisions,
  incidents, rollback or recovery actions, and cleanup ownership.

## Context management and continuity

Optional context tools include [project-context](https://github.com/monomind-ai-lab/project-context)
and [project-hub](https://github.com/monomind-ai-lab/project-hub). Use the
repository's approved context locations; these tools are not prerequisites.

- Keep durable truth in repository-owned specifications, decisions, current
  project context, task records, and evidence—not only in chat transcripts or
  one agent's memory.
- Define authoritative locations and an owner for freshness. Link to sources
  instead of copying them into competing summaries.
- Update the task record at meaningful state changes and before compaction,
  session transfer, long pauses, or handoff. Include objective, scope, exact
  branch/revision, changed files, decisions, checks actually run, evidence,
  blockers, and one next executable step.
- A resuming agent verifies repository and external state before acting; it does
  not assume a handoff or historical summary is still current.
- Keep secrets, personal data, private endpoints, and irrelevant host-specific
  paths out of shared continuity artifacts.
