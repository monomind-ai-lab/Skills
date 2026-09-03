---
name: monomind-workflow
description: "Adopt or run Monomind's end-to-end code-task workflow: isolate, build, prove, and ship. Use when setting up a repository's agent workflow, starting a new feature or fix, coordinating concurrent agents, or taking an issue or specification through implementation and a pull-request handoff. Use narrower skills for read-only or already-isolated single-phase work."
---

# Monomind Workflow

Coordinate a complete code task through four beats. The beats are gates, not automatic permission: local implementation, Git mutations, remote publication, review replies, and merge each follow the authority supplied by the user and project.

Installing this folder makes the workflow discoverable; it does not make the rules persistent. Repository adoption is the separate step that places mandatory routing in the active root `AGENTS.md` and project facts in `.monomind/workflow.md`.

## Select the mode

- **Adopt:** the user wants a repository to encode this workflow for future agents. Read [references/project-profile.md](references/project-profile.md), inspect the repository, use the bundled `scripts/adopt.py` for the managed instruction block and profile scaffold, then fill the profile only from verified project evidence.
- **Run:** the user is starting a feature, fix, or code-changing task, or wants one issue or specification carried end to end. Follow all four beats below; stop the Ship beat at the furthest authorized destination.

Do not invoke the full workflow for a read-only question, review-only request, evidence-only request, or work already isolated and explicitly scoped to one downstream phase. Those stay with the phase-specific workflow.

In Run mode, use an installed phase skill only when its narrower trigger applies:

- Before Build: `monomind-intake`, `monomind-spec`, or `monomind-plan` for unresolved intent, contract, or task ordering.
- During Build: `monomind-design` for a boundary decision, `monomind-build` for the slice loop, and `monomind-debug` for an unexpected failure.
- During Prove: `monomind-evidence`, plus `monomind-before-after` for a visible UI claim.
- During Ship: `monomind-review`, `monomind-release`, or `monomind-handoff` when the delivery state calls for them.

The conductor remains self-contained when one of those skills is absent; do not stop merely to install an optional phase skill.

## Preflight the task

1. Read local instructions, the task or spec, repository state, current branch/worktree, and configured remotes.
2. Verify the factory base `origin/main`, task owner, acceptance claims, repository checks, and delivery target. When this skill is project-installed, its bundled `scripts/adopt.py preflight --repo <repository>` provides the deterministic branch/worktree portion of this check. If `origin/main` does not exist, stop and require a recorded repository exception instead of silently substituting another base.
3. Map authority for workspace creation, dependency installation, commits, history changes, pushes, review replies, PR creation, and merge. Use authority already explicit in the request or project; ask only for a missing permission when the beat reaches that action.
4. Scale the ceremony to risk. A small self-contained task still crosses the gates, but its artifacts can be compact.

## Beat 1: Isolate

Establish an exclusive, recoverable workspace before editing.

1. Preserve unknown local changes and inspect other worktrees or task ownership.
2. Every implementation task runs in a fresh task worktree and branch based on the latest `origin/main`; never build on `main`. A harness-managed worktree satisfies this gate when it is exclusive to the task and its base is verified. Otherwise fetch `origin` and create a uniquely named worktree through the repository convention. If fetching or workspace creation is not authorized, stop before editing.

   ```bash
   git fetch origin
   git worktree add <gitignored-worktrees-dir>/<task-name> \
     -b <branch-prefix>/<task-name> origin/main
   git -C <gitignored-worktrees-dir>/<task-name> branch --show-current
   ```

   The final command must name the new task branch, never `main`. If the worktree or branch name already exists, choose a fresh task name instead of forcing or reusing it.
3. If the remote/task system is available and in scope, compare likely files with active changes. Surface a real overlap before both efforts diverge.
4. Allocate shared resources—ports, databases, queues, caches, test accounts, and generated lockfiles—because worktrees do not isolate them. Verify that any running service answers from this task's code.

The beat is complete when the task has one known owner, workspace, base, scope boundary, and shared-resource assignment.

## Adopt the workflow into a repository

Use this procedure only in Adopt mode:

1. Ensure `monomind-workflow` is installed project-locally. A global-only copy cannot establish shared team behavior.
2. Create or enter a fresh linked task worktree based on `origin/main`; adoption is not an exception to the isolation rule.
3. Locate this skill's installed directory and run:

   ```bash
   python3 <skill-dir>/scripts/adopt.py apply --repo <repository>
   ```

   The script preserves all text outside its managed markers. It updates a non-empty root `AGENTS.override.md` when that file shadows `AGENTS.md`; otherwise it updates or creates root `AGENTS.md`. It never replaces an existing workflow profile.
4. Inspect repository instructions, manifests, CI, tests, and runtime configuration. Replace values marked `UNRESOLVED` in `.monomind/workflow.md` only when repository evidence establishes the answer. Leave genuine unknowns visible.
5. Run `python3 <skill-dir>/scripts/adopt.py check --repo <repository>`, inspect the complete diff, and report any unresolved profile fields. Do not commit or publish unless separately authorized.

Do not silently add a lifecycle hook. Skill selection, persistent `AGENTS.md` instructions, Codex hooks, Git hooks, CI, and branch protection are distinct layers. Add a hook only when the user or project explicitly selects that host-specific enforcement and its trust path.

## Beat 2: Build

Deliver the behavior in thin, verified slices.

1. Turn the acceptance claims into the smallest complete behavior slice and a public test seam.
2. Establish a red signal for changed behavior, implement the simplest complete path, clean locally while green, and run repository-native focused checks.
3. Use the service-layer boundary for side-effecting workflows: actions or boundaries own domain policy, authorization, state transitions, and **why/when** an operation runs; services or capabilities own the reusable **how**, with explicit inputs, structured returns, and typed failures. Keep one-off mechanics local until reuse or a volatile external boundary earns extraction—do not create a pass-through service for ceremony.
4. Keep the diff inside the assigned task. Record adjacent improvements instead of absorbing them.
5. Stop feature expansion on an unexpected failure and enter a reproducible root-cause loop.

The beat is complete when the approved behavior exists through a public seam and the repository remains valid.

## Beat 3: Prove

Build the delivery evidence while the task context is still fresh.

1. Map every material acceptance claim to a repository check or runtime artifact.
2. Capture the failing **before** state for a bug or regression before fixing it whenever feasible; capture the matched **after** state once the change works. For a visible UI change, use `monomind-before-after` when installed to produce the verified pair and PR-ready Markdown; otherwise preserve equivalent matched local captures.
3. Run the relevant full gates after the final edit. Bind runtime proof to the exact revision, environment, data class, and reproduction sequence.
4. Keep artifacts local and private by default. Mark claims passed, failed, or untested with a reason; publication is a Ship action.

The beat is complete when every acceptance claim has trustworthy evidence or an explicit gap.

## Beat 4: Ship

Package and publish only as far as authorized.

1. Inspect the final diff for scope, secrets, weakened checks, generated noise, and unintended files.
2. Reconcile with the authoritative base using the repository's integration strategy, then rerun affected checks. Never rewrite a shared or protected branch; avoid history rewriting unless the user and project selected it for this owned task branch.
3. When authorized, commit only task files, push the owned branch, and open the configured change request. Otherwise produce a local, PR-ready handoff.
4. The change description states outcome, scope, acceptance evidence, exact checks, before/after proof where relevant, risks, follow-up work, and rollback implications. Visible changes include the verified before/after table when publication is authorized.
5. Run the repository's CI and review loop. Address actionable blocking findings, rerun affected proof, and update the change. Stop and escalate when feedback contradicts the spec or project rules, expands scope, or repeats after a good-faith fix without new evidence.
6. Present the change URL or local handoff. Merge only when the user explicitly authorizes merge.

Keep task isolation until the change is merged, closed, or deliberately handed off. Clean it up through the repository or harness mechanism, never by deleting another owner's work.

## Cross-agent invariants

- One task owner, owned workspace, and owned delivery branch at a time.
- Never modify, stash, reset, rebase, or delete another owner's unknown work.
- Regenerate generated lockfiles from their canonical tool instead of hand-merging conflicting output.
- Trace conflict intent to both authoritative sources; report unresolved ambiguity instead of guessing.
- Remote review scores and bots are evidence sources, not the definition of done. Completion follows the spec, project gates, and resolved blocking findings.

## Hold the gates under pressure

| Temptation | Required response |
| --- | --- |
| "The skills are installed, so adoption is unnecessary." | Installation exposes lazy metadata. Persist the mandatory trigger in repository instructions before calling the factory adopted. |
| "This edit is tiny or urgent, so main is fine." | Collision risk begins with the first edit. Create the owned worktree before changing files. |
| "I will not commit on main, so editing there is harmless." | Uncommitted edits still collide with people and agents. Isolation is an editing precondition, not a commit check. |
| "Every action deserves a service wrapper." | Extract reusable or volatile mechanics; keep one-call pass-throughs out. |
| "Tests passed, so a UI screenshot is optional." | Tests and visual proof answer different claims. Capture a matched pair for a material visible change. |

## Completion criteria

In **Adopt** mode:

- The project-local workflow skill, managed instruction block, workflow profile, and `origin` configuration pass the bundled check.
- Existing instructions and profile content remain intact outside the managed addition, and unknown project facts remain visibly unresolved.
- The handoff identifies changed files, unresolved profile values, the new-task activation boundary, and any separate commit or publication authority.

In **Run** mode:

- All four beats have a visible completion condition and evidence.
- Workspace, branch, remote, and shared-resource ownership are unambiguous.
- Every acceptance claim is proven or explicitly untested.
- The published or local handoff contains the exact checks, artifacts, risks, and next state.
- No remote mutation or merge exceeded the task's authority.
