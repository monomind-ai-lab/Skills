# Curation record

This record explains what was learned from each source, what entered the Monomind collection, and what was intentionally left out. The upstream repositories were inspected as temporary source material; none is a parent remote, subtree, or vendored snapshot of this repository.

## Audited revisions

| Source | Revision inspected | Upstream license | Primary contribution to the synthesis |
| --- | --- | --- | --- |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | `d2c37ef6225dd8726cdd369a8030307f48592d26` (2026-08-28) | MIT | Lifecycle coverage, assumption surfacing, gated specs, vertical slices, per-skill verification, multi-axis review, source verification, reversible rollout, catalog evals |
| [`mattpocock/skills`](https://github.com/mattpocock/skills) | `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76` (2026-08-24) | MIT | Small composable skills, progressive disclosure, domain language, deep modules and test seams, tracer-bullet tickets, spec-vs-standards review, tight debugging loops, pointer-based handoffs |
| [`michaelshimeles/skills`](https://github.com/michaelshimeles/skills) | `5d403ea66775c04df222a1e9b302ef64ae45c712` (2026-09-01) | No repository-wide license found; `before-and-after/` is PolyForm Shield 1.0.0 | Benchmark for its `AGENTS.md` four-beat workflow, worktree isolation, action/service separation, evidence captured during implementation, and before/after PR proof |

Access date: 2026-09-02.

Detailed benchmark analysis: [`docs/benchmarks/michaelshimeles-agents.md`](benchmarks/michaelshimeles-agents.md).

The Michael Shimeles repository was used only to study ideas and workflow shape. Its unlicensed root material, including `AGENTS.md`, was not copied. Its `before-and-after` software and skill text were not copied or redistributed; Monomind's original integration invokes the external [`@vercel/before-and-after`](https://www.npmjs.com/package/@vercel/before-and-after) package under its PolyForm Shield 1.0.0 license. Its Greptile-specific MIT subtrees remain excluded because they are vendor-specific rather than factory primitives.

## Selection matrix

| Factory need | Adopted synthesis | Sources that most influenced it |
| --- | --- | --- |
| Intent alignment | Outcome hypothesis plus a dependency-aware decision frontier and explicit non-goals | Addy's `interview-me`; Matt's `grilling` |
| Specification | Living behavioral contract, selective capability maps, public seams, and sparse ADRs | Addy's spec/ADR skills; Matt's `to-spec`, domain modeling, and codebase design |
| Planning | Tracer-bullet vertical tasks with blocking edges; expand–migrate–contract for wide refactors | Addy's task breakdown; Matt's `to-tickets` and wayfinding concepts |
| End-to-end task workflow | A narrowly triggered Isolate → Build → Prove → Ship conductor with deterministic repository adoption, project profiling, shared-resource ownership, authority checkpoints, and PR-ready completion | Michael's `AGENTS.md`, rewritten for Monomind portability and authority boundaries |
| Architecture | Deep modules plus a policy/mechanics split with explicit capability inputs and structured results | Matt's codebase design; Michael's code-structure skill |
| Implementation | Repository-native discovery, red/green/clean slices, current primary sources, scope discipline, and diff inspection | Addy's incremental/TDD/source-driven workflows; Matt's seam-focused TDD |
| Diagnosis | A tight red feedback loop, minimization, falsifiable hypotheses, boundary instrumentation, and regression proof | Addy's debugging workflow; Matt's diagnosing-bugs skill |
| Evidence | Match each acceptance claim to the cheapest trustworthy artifact and bind it to revision/environment | Michael's evidence-driven testing and before/after concepts; Addy's runtime verification |
| Visual PR proof | Matched URL/image/element captures, controlled viewports, PR-ready Markdown, and explicit public-upload authority through an external licensed CLI | Michael's `before-and-after` integration pattern and the external `@vercel/before-and-after` package |
| Review | Fixed comparison point; independent spec-fidelity and standards axes; prioritized findings | Matt's two-axis review; Addy's correctness/readability/architecture/security/performance review |
| Release | Evidence-based gates, project-derived thresholds, observability questions, staged exposure, executable rollback | Addy's shipping and observability skills |
| Continuation | Compact state with verified repository facts and pointers instead of duplicated artifacts | Matt's handoff and writing-for-agents skills |
| Quality of the collection | Structural and routing evals with realistic positive/negative prompts and behavioral expectations | Addy's three-tier eval approach; Matt's trigger-focused descriptions |

## Conflict resolutions

| Upstream tension | Monomind decision |
| --- | --- |
| Ask one interview question at a time vs. ask a whole frontier | Ask one when the answer changes downstream questions; batch only mutually independent frontier decisions. Every question carries a recommendation and tradeoff. |
| Refactor during every TDD cycle vs. defer refactoring to review | Permit small local cleanup while green; keep architectural and wide refactors as separately planned work. |
| Commit every increment | Verify every increment, but commit only when the user's and repository's authority covers it. |
| Start every implementation task in a new worktree from `origin/main` | Use the approved authoritative base; `origin/main` remains the bootstrap default. A harness-managed worktree qualifies when exclusive and base-verified. The checker consumes recorded alternatives rather than requiring a prose-only exception. Never build on the protected base. |
| Every task follows the full four-beat ceremony | Apply the conductor to every newly started code-changing feature or fix, using compact artifacts for small work. Read-only and already-isolated downstream phases stay with smaller skills. |
| Rebase, push, open a PR, and iterate a vendor score automatically | Treat local edits, history changes, pushes, change requests, review replies, and merge as distinct authority gates. Review completes on project gates and resolved blockers, not a vendor score. |
| Publish specs and tickets directly to an issue tracker | Use the configured canonical target, but require authority for external tracker mutations; default to a proposed local artifact. |
| Always create extensive specs and task trees | Scale ceremony to ambiguity, risk, and dependency structure; skip intake/spec/plan for mechanical self-evident work. |
| Require subagents for testing or review | Preserve independent axes and evidence requirements without requiring a particular orchestration mechanism. |
| Use generic rollout percentages and thresholds | Derive gates from SLOs, historical baselines, contracts, or an explicit decision. |
| Upload visual proof as part of evidence capture | Support PR-ready Markdown through `@vercel/before-and-after`, but verify local artifacts first and require authority for the package download, public/default upload, custom upload destination, and PR mutation. |
| Put shared checklists at repository root | Keep each installable skill self-contained so individual installation does not break references. |
| Installing a skill makes its principles automatic | Separate availability from adoption: skill metadata routes lazily, a managed `AGENTS.md` block supplies persistent mandatory rules, and a deterministic script checks policy/profile drift. Hooks and CI remain separate explicit controls. |

## Intentionally excluded

- Broad always-on meta-routing that adds context to unrelated tasks. The adopted root instruction block contains only mandatory cross-cutting invariants and one workflow trigger.
- Vendor-specific Greptile loops, issue-tracker setup, and silently installed lifecycle hooks. The Vercel before/after CLI is integrated narrowly because the user selected it as a factory primitive.
- Upstream scripts, screenshots, fixtures, and source trees.
- Vendored PolyForm Shield software and unlicensed upstream expression. The external PolyForm package is referenced and invoked without redistribution.
- Universal file-count, line-count, coverage, rollout-percentage, or timing rules presented as facts.
- Automatic commits, pushes, messages, issue creation, package installation, public upload, or production mutation. Fresh worktree creation is the explicit Isolate beat of an end-to-end implementation workflow.
- In-progress, course-authoring, and personal utility skills that do not generalize to a software factory phase.

## Maintenance rule

Upstream changes are research inputs, not updates to merge. A curator may re-audit a newer revision, record what decision-relevant idea changed, and make a fresh Monomind edit with its own tests and provenance. Never replace this collection with an upstream tree or make one of the sources its Git parent.
