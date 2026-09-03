---
name: monomind-onboarding
description: "Complete or audit .monomind/workflow.md through a repository-owner or project-lead policy interview. Use when the profile is absent, contains UNRESOLVED values, needs explicit collaboration, integration, test, CI/CD, release, or continuity decisions, or fails a policy readiness gate. Do not use once the profile passes or to execute code tasks."
---

# Monomind Repository Onboarding

Turn repository evidence and owner-approved policy decisions into a complete
`.monomind/workflow.md`. This is a policy interview, not an implementation task.
Read [references/policy-principles.md](references/policy-principles.md) before
proposing policy choices.

Every `UNRESOLVED` field is a deliberate stop marker. An agent may discover
facts, explain tradeoffs, and draft a proposal, but only the repository owner,
project lead, or an explicitly named delegate may define or approve repository
policy. Do not silently convert convention, absence of configuration, or a
likely default into policy.

## Establish the onboarding boundary

1. Identify the repository root, current branch and worktree, active local
   instructions, existing `.monomind/workflow.md`, and the person authorized to
   approve repository policy.
2. Treat writing or changing the profile as a repository change. Work from a
   fresh task-owned linked worktree based on `origin/main`, never from `main` or
   another task's workspace. Preserve unrelated and existing profile content.
3. If the approver's authority is unclear, ask whether they are the repo owner,
   project lead, or named delegate. Without an authorized approver, continue as
   a read-only discovery and draft exercise; leave policy decisions
   `UNRESOLVED` and state who must decide them.
4. Installation does not itself authorize commits, pushes, pull requests,
   merges, deployments, package installation, or remote configuration changes.

## Discover before asking

Inspect the smallest relevant checked-in evidence first:

- root and nested instructions, README/contributor docs, ownership files, and
  existing decision or task records;
- Git remotes, branch conventions, merge documentation, and change-request
  templates;
- manifests, task runners, test configuration, linters, type checks, build
  tools, smoke checks, and generated-file rules;
- checked-in CI/CD workflows, release configuration, environment promotion,
  migration and rollback material, and branch-protection documentation;
- evidence directories, data/privacy rules, visual targets, shared ports,
  databases, queues, caches, emulators, and test-account conventions; and
- continuity sources: specifications, ADRs, project context, task records,
  handoff locations, and their expected update triggers.

Classify each profile field before the interview:

- **Verified fact:** mechanically established by repository evidence. Cite the
  file, command, or configured remote that establishes it.
- **Policy decision:** requires explicit owner/lead approval even when the
  repository suggests a likely answer.
- **Not applicable:** allowed only as `NOT_APPLICABLE — <specific reason>` when
  evidence or the authorized approver establishes why.
- **Unresolved blocker:** no verified answer or approval exists. Keep
  `UNRESOLVED` visible and name the decision owner.

The absence of a CI file does not prove that CI is optional. A common command
does not prove that it is required. Ask instead of guessing.

## Run the owner or lead interview

Present verified facts first, including their evidence, then ask only about the
remaining decisions. Group questions into short rounds and write confirmed
answers after each round so the interview is resumable:

1. **Ownership and collaboration:** policy approver, task assignment, parallel
   work and overlap handling, shared-resource coordination, reviewers,
   escalation, and cleanup authority.
2. **Integration:** authoritative base and change-request target, branch and
   worktree naming, merge/rebase/squash strategy, required approvals, merge
   authority, and whether any history rewrite is permitted.
3. **Testing and CI/CD:** exact setup and focused/regression/type/lint/build/
   smoke commands, required CI gates and triggers, retry or override authority,
   and which failures block integration.
4. **Release:** environments and promotion path, release pipeline, owner and
   approver, required evidence, migration and rollback procedure, observation
   window, and who may release under which explicit instruction.
5. **Evidence, safety, and continuity:** artifact and publication locations,
   test-data and capture restrictions, authoritative context and decision
   records, handoff format, update triggers, and freshness ownership.

When offering options, state the operational tradeoff and label the answer as a
proposal until the approver explicitly accepts it. Do not pressure the approver
to choose a Monomind recommendation when project constraints require another
recorded rule.

## Write the repository profile

If adoption has not created the profile and `monomind-workflow` is installed
project-locally, use its bundled scaffold without overwriting existing content:

```bash
python3 <monomind-workflow-skill-dir>/scripts/adopt.py apply --repo <repository>
```

If the workflow skill is unavailable, create `.monomind/workflow.md` with the
same policy areas listed above and mark every unknown value `UNRESOLVED`; report
that persistent `AGENTS.md` adoption is still outstanding.

When a profile already exists, compare its field labels with the installed
workflow template. Insert newly introduced fields under their matching sections
as `UNRESOLVED`; never replace the file wholesale or reset previously approved
values during a schema refresh.

Update only fields established in the current interview or by cited evidence.
Use one of these forms:

```text
<verified value> — evidence: <project-relative path or command>
<policy value> — approved by <role/name>, <YYYY-MM-DD>; decision: <path or URL>
NOT_APPLICABLE — <specific approved or evidenced reason>
UNRESOLVED — decision required from <role>
```

Do not put credentials, private endpoints, personal data, or machine-specific
home paths in the shared profile. Prefer project-relative pointers over copying
large policy documents. Preserve prior approved values unless the approver
explicitly supersedes them, and record the new approval reference and date.

## Certify readiness

When the workflow skill is available, run the structural check, then the
appropriate policy gate:

```bash
python3 <monomind-workflow-skill-dir>/scripts/adopt.py check --repo <repository>
python3 <monomind-workflow-skill-dir>/scripts/adopt.py check --gate build --repo <repository>
python3 <monomind-workflow-skill-dir>/scripts/adopt.py check --gate release --repo <repository>
```

- **Build-ready** means the owner/lead, task and workspace model, naming,
  project setup, focused and regression checks, architecture boundary, shared
  resources, continuity sources, and mutation authority are resolved.
- **Release-ready** includes Build-ready and requires the complete current
  profile: integration, all applicable checks, CI/review, evidence, security,
  release/rollback, context, and approval fields contain no unresolved or bare
  not-applicable value.

Do not call a repository Build-ready or Release-ready when the corresponding
gate fails. Report the remaining field names, their decision owner, changed
files, evidence inspected, and the next exact approval needed. Commit or publish
the onboarding change only when separately authorized.

## First-run activation boundary

When delivered through the Monomind Codex plugin, a reviewed `SessionStart`
hook can add context that routes the first repository task here while the
profile is absent or unresolved. The hook cannot start a conversation during
installation, answer policy questions, or authorize writes. It stays silent
after the profile has no unresolved fields. Skills-CLI installations have no
install-time hook, so invoke this skill explicitly after installation.
