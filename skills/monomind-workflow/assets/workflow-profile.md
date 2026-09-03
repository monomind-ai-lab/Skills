# Monomind workflow profile

This file records the project-specific facts and policies used by the Monomind
skills. Every `UNRESOLVED` value is a deliberate stop marker: it must be defined
for this repository and approved by its repository owner, project lead, or an
explicitly named delegate. Agents may inspect evidence and draft options, but
they must not invent or approve policy.

Replace a field with a verified value plus its project-relative evidence, an
owner-approved decision plus approval date/reference, or
`NOT_APPLICABLE — <specific reason>`. Do not use a bare `N/A` or
`NOT_APPLICABLE`. Ownership and approval fields cannot be not-applicable. Run
`$monomind-onboarding` to complete or refresh this file.

## Ownership and approval

- Repository owner or project lead: UNRESOLVED
- Approved policy decision-maker(s): UNRESOLVED
- Policy approval record and date: UNRESOLVED
- Profile maintainer and review trigger: UNRESOLVED

## Collaboration

- Task ownership and assignment source: UNRESOLVED
- Parallel work and overlap coordination: one named owner, branch, and worktree per task; identify likely overlap before work diverges
- Worktree cleanup authority: UNRESOLVED
- Communication and escalation path: UNRESOLVED

## Integration

- Authoritative base branch: `origin/main`
- Integration strategy: UNRESOLVED
- Task isolation: fresh task-owned Git worktree and branch from `origin/main`; never implement on `main` or in another task's worktree
- Branch/worktree naming convention: UNRESOLVED
- Canonical remote and change-request target: UNRESOLVED
- History rewrite policy: never rewrite shared or protected history; owned-task exceptions require an explicit recorded decision

## Repository checks

- Environment setup: UNRESOLVED
- Focused test: UNRESOLVED
- Full regression suite: UNRESOLVED
- Type or compile check: UNRESOLVED
- Lint and format check: UNRESOLVED
- Build/package check: UNRESOLVED
- Runtime or smoke check: UNRESOLVED

## Architecture, safety, and compatibility

- Security and privacy: UNRESOLVED
- Architecture and dependency direction: actions/boundaries own policy and why/when; services/capabilities own reusable how through explicit inputs, structured returns, and typed failures
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

- Shared-resource isolation and allocation: UNRESOLVED
- How to verify a running service belongs to the current task: UNRESOLVED

## CI/CD, change request, and review

- Required change-description sections: UNRESOLVED
- Required CI gates and trigger conditions: UNRESOLVED
- Human or automated reviewers: UNRESOLVED
- Blocking-finding policy: UNRESOLVED
- CI retry, rerun, and override authority: UNRESOLVED
- Who may merge and under what instruction: UNRESOLVED

## Release

- Release environments and promotion path: UNRESOLVED
- Release command or pipeline: UNRESOLVED
- Release owner and approver: UNRESOLVED
- Required release evidence: UNRESOLVED
- Rollback or recovery procedure: UNRESOLVED
- Post-release verification and observation window: UNRESOLVED
- Who may release and under what instruction: UNRESOLVED

## Context management and continuity

- Context pipeline: [project-context](https://github.com/monomind-ai-lab/project-context) (repo-level) and [project-hub](https://github.com/monomind-ai-lab/project-hub) (org-level)
- Authoritative project context and decision records: UNRESOLVED
- Task and handoff location and required contents: UNRESOLVED
- Context update triggers: before compaction, session transfer, long pause, or handoff, and after a material decision or verification result
- Context freshness owner and review cadence: UNRESOLVED
- Resumption verification: reread authoritative repository state and confirm branch, revision, checks, blockers, and external status before acting

## Authority defaults

- Actions agents may take without a new prompt: read-only repository inspection and project-approved local checks
- Actions requiring explicit user instruction: UNRESOLVED

## Readiness gates

The structural check may pass while onboarding remains incomplete. Build and
Release agents must use the corresponding gate and stop on failure:

```bash
python3 <monomind-workflow-skill-dir>/scripts/adopt.py check --gate build --repo .
python3 <monomind-workflow-skill-dir>/scripts/adopt.py check --gate release --repo .
```
