# Monomind workflow profile

This file records repository facts used by the `monomind-workflow` skill (in
Codex: `$monomind-workflow`). Replace `UNRESOLVED` only with values verified
from this repository. Keep an unresolved value visible when the repository does
not establish an answer.

## Delivery topology

- Authoritative base branch: `origin/main`
- Integration strategy: UNRESOLVED
- Task isolation: fresh task-owned Git worktree and branch from `origin/main`
- Branch/worktree naming convention: UNRESOLVED
- Canonical remote and change-request target: UNRESOLVED

## Repository checks

- Environment setup: UNRESOLVED
- Focused test: UNRESOLVED
- Full regression suite: UNRESOLVED
- Type or compile check: UNRESOLVED
- Lint and format check: UNRESOLVED
- Build/package check: UNRESOLVED
- Runtime or smoke check: UNRESOLVED

## Hard invariants

- Security and privacy: UNRESOLVED
- Architecture and dependency direction: actions/boundaries own policy and why/when; services/capabilities own reusable how through explicit inputs and structured returns
- Data compatibility and migrations: UNRESOLVED
- Performance or reliability budgets: UNRESOLVED
- Generated files and lockfiles: UNRESOLVED

## Evidence

- Gitignored local artifact path: UNRESOLVED
- Test data and account policy: UNRESOLVED
- UI/runtime targets and viewports: UNRESOLVED
- Sensitive surfaces that must not be captured: UNRESOLVED
- Approved publication destinations: UNRESOLVED

## Shared resources

- Port allocation: UNRESOLVED
- Database/schema isolation: UNRESOLVED
- Queues, caches, buckets, emulators, and test accounts: UNRESOLVED
- How to verify a running service belongs to the current task: UNRESOLVED

## Change request and review

- Required change-description sections: UNRESOLVED
- Required CI gates: UNRESOLVED
- Human or automated reviewers: UNRESOLVED
- Blocking-finding policy: UNRESOLVED
- Who may merge and under what instruction: UNRESOLVED

## Authority defaults

- Actions agents may take without a new prompt: read-only repository inspection and project-approved local checks
- Actions requiring explicit user instruction: UNRESOLVED
