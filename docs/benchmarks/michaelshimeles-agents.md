# Benchmark review: michaelshimeles/skills `AGENTS.md`

## Verdict

The benchmark's strongest contribution is not any individual command; it is a memorable end-to-end contract that makes isolation, architecture, proof, and delivery one continuous task. Monomind should retain that four-beat shape while replacing repository-specific tools and implicit external authority with explicit factory rules.

Reviewed source: [`michaelshimeles/skills`](https://github.com/michaelshimeles/skills) at `5d403ea66775c04df222a1e9b302ef64ae45c712` on 2026-09-02. The repository had no root license at that revision. This document analyzes ideas and uses original wording; it does not reproduce the upstream file.

## What the benchmark gets right

### One lifecycle agents can remember

**Isolate → Build → Prove → Ship** gives every task the same high-level state machine. The completion condition of one beat becomes the precondition of the next, preventing implementation from silently skipping workspace safety, runtime proof, or delivery hygiene.

### Isolation is a first-class engineering step

The benchmark treats a worktree as part of correctness rather than convenience. One task and agent own one workspace and branch; active pull requests and unknown local changes are checked before editing; ports, databases, and lockfiles are recognized as shared even when files are isolated.

### Architecture is stated as an ownership rule

The action/service split is concise enough to apply while coding:

- actions and boundaries own domain meaning, policy, and why or when an operation happens;
- services and capabilities own reusable operational mechanics, with explicit inputs and structured results.

That is more actionable than a generic instruction to use clean architecture. Monomind adds one guard: do not create a pass-through service until reuse or a volatile external boundary makes extraction valuable.

### Evidence is gathered when it is cheapest

Capturing the failing before state during reproduction avoids reconstructing it after the fix. Reusing those artifacts in the pull request joins verification and communication instead of creating a second documentation exercise at the end.

### Completion is operationally concrete

The benchmark defines a finish line: checks, evidence, integration with the base, commit, push, pull request, review loop, and final URL. It also correctly keeps merge as a separate explicitly authorized action.

### Repositories supply their own facts

The extension points for exact commands, invariants, environment notes, fixtures, and locally untestable behavior keep the portable workflow from guessing project details.

## What Monomind changes

| Benchmark behavior | Monomind treatment |
| --- | --- |
| Hardcode the complete workflow in every repository `AGENTS.md` | Put the detailed behavior in `monomind-workflow`; use its idempotent adoption script to preserve existing instructions while installing a short mandatory trigger block plus a verified repository profile. |
| Fresh worktree from `origin/main` and no work on `main` | Adopted as the factory default. Harness-managed isolation qualifies when it is task-exclusive and base-verified; repositories need an explicit recorded exception if `origin/main` cannot exist. |
| Apply a service layer to builds | Adopt the why/when versus reusable-how ownership rule, with explicit inputs and structured results; avoid ceremonial one-call services. |
| Use `@vercel/before-and-after` for PR visuals | Add `monomind-before-after` as an original integration skill. The external package is not vendored and remains under PolyForm Shield 1.0.0. |
| Upload with Markdown mode | Support it for approved public captures or an approved custom upload destination. Local verification comes first; publication authority is separate. |
| Always commit, rebase, push, and open a PR | Treat each as a distinct delivery action covered by the user's request or project policy. Without remote authority, stop at a complete PR-ready local handoff. |
| Reach a Greptile score of 5/5 | Use repository CI and review sources, resolving blocking evidence-backed findings. Do not make one vendor score the definition of done. |
| Rebase and use force-with-lease after push | Follow the repository's integration strategy. Never rewrite shared/protected history; rewrite an owned branch only when explicitly selected and safe. |
| Run the whole ceremony for every request | Trigger the conductor for every newly started code-changing feature or fix, plus workflow adoption and concurrent-agent coordination. Read-only and already-isolated downstream phases use narrower skills. |

## Resulting skill topology

| Beat | Primary skill | Supporting skills |
| --- | --- | --- |
| Isolate | `monomind-workflow` | Repository workflow profile |
| Build | `monomind-workflow` | `monomind-build`, `monomind-design`, `monomind-debug` |
| Prove | `monomind-workflow` | `monomind-evidence`, `monomind-before-after` |
| Ship | `monomind-workflow` | `monomind-review`, `monomind-release`, `monomind-handoff` |

`monomind-workflow` is self-contained enough to run alone. When the narrower collection skills are installed, it routes specialized work to them without making them always-on context.

Installation and adoption are intentionally distinct. Installing the folder exposes only the skill's routing metadata until it is selected. Adoption adds the persistent repository instruction block that requires the workflow before implementation and creates `.monomind/workflow.md` for repository-native facts. No lifecycle hook is silently enabled; hooks, Git controls, CI, and branch protection remain explicit enforcement layers.

## Benchmark acceptance checks

The adaptation counts as successful when:

- an end-to-end task cannot reach implementation while still on `main`;
- adoption itself refuses `main`, detached HEAD, the primary checkout, and a task branch not based on the locally available `origin/main`;
- existing repository instructions and an existing workflow profile survive repeated adoption unchanged outside one managed block;
- a deterministic check detects a missing project skill, policy drift, missing profile, or missing `origin` configuration;
- the owned worktree is based on the latest verified `origin/main` or an explicit repository exception blocks/provides an alternative;
- concurrent work and shared runtime resources are checked before editing;
- side-effecting workflows preserve the why/when versus reusable-how ownership split;
- a bug's before state is captured before the fix when feasible;
- visible UI changes produce a controlled before/after pair and a PR-ready table when publication is authorized;
- package installation, upload, commit, push, PR mutation, review replies, and merge never inherit authority from one another;
- delivery ends with a verifiable change URL or a complete local handoff, never an unsupported claim of completion.
