---
name: monomind-review
description: "Review a branch, diff, pull request, or worktree against both its originating specification and repository engineering standards. Use before merge or when the user asks for code review, quality assessment, or regression risk. Review is read-only unless fixes are separately requested."
---

# Monomind Review

Pin the comparison, reconstruct intent, and review on two independent axes: **spec fidelity** and **engineering quality**.

## Frame the review

1. Identify the fixed comparison point: explicit commit, merge base, branch, tag, or the current staged/unstaged diff. State any ambiguity.
2. Read the originating spec, issue, or request and its acceptance criteria. If none exists, reconstruct the claimed behavior from the user's request and change description.
3. Read repository standards, local instructions, domain vocabulary, relevant decisions, and the verification commands that gate the affected area.
4. Inventory changed files and generated artifacts. Separate change-introduced problems from pre-existing ones.

## Axis A: spec fidelity

Check whether the change:

- delivers every required behavior and no unapproved expansion;
- preserves explicit non-goals and compatibility constraints;
- handles normal, boundary, failure, and recovery scenarios;
- supplies evidence for each acceptance claim;
- updates the spec when a deliberate implementation discovery changed the contract.

## Axis B: engineering quality

Review tests first, then implementation:

- **Correctness:** invariants, state, errors, concurrency, boundary conditions, and regression coverage.
- **Simplicity:** readable flow, domain vocabulary, no speculative abstraction or dead indirection.
- **Architecture:** ownership, dependency direction, deep public seams, and policy/mechanics separation.
- **Security and privacy:** trust boundaries, authorization, validation, secrets, injection, and data exposure.
- **Performance and reliability:** unbounded work, query patterns, hot paths, retries, timeouts, and resource cleanup.
- **Operability:** diagnostic signal, failure visibility, migration safety, rollback, and flag lifecycle where relevant.
- **Change hygiene:** focused diff, dependency and lockfile review, generated files, and no weakened gates.

Verify material test/build claims when the environment permits. A green suite is evidence, not proof that the tests exercise the right behavior.

## Report findings first

Use these priorities:

- **P0:** immediate security, privacy, data-loss, or production-wide failure risk.
- **P1:** incorrect required behavior or a likely serious regression.
- **P2:** maintainability, reliability, or operability defect worth fixing before merge.
- **P3:** optional improvement or minor clarity issue.

Each actionable finding names the location, evidence, user or system impact, and the smallest credible remedy. Order by severity and leverage; do not bury a structural or correctness problem under stylistic comments.

Conclude with the verification observed, residual risks, and a verdict. When there are no findings, say so directly and name what was not verified. Do not edit the change unless the user asks for fixes.

## Completion criteria

- The fixed point, spec source, standards sources, and reviewed surface are explicit.
- Spec and standards axes were both evaluated without substituting one for the other.
- Findings are actionable, prioritized, and tied to evidence and impact.
- Pre-existing issues and unverified assumptions are separated from change-introduced defects.
- The verdict follows from the findings and observed verification.
