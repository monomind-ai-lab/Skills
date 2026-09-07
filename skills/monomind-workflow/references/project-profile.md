# Adopt the repository workflow

Use this reference only for adoption, profile migration, or hook configuration.

## Install and isolate

A project-local copy of monomind-workflow makes the scripts and policy travel
with the repository. Supported locations are .agents/skills, .claude/skills,
and .factory/skills. Global/plugin installation alone does not establish team
policy. Do not install missing packages unless the request authorizes it.

Inspect existing instructions and approved base. Create or reuse an exclusive
linked task worktree from that base; origin/main is the initial default.
Use a named task branch, never main or the configured protected base branch.

## Apply

Run the installed script:

```bash
python3 <skill-dir>/scripts/adopt.py apply --repo <repository>
# Initial adoption with an explicitly approved alternative:
python3 <skill-dir>/scripts/adopt.py apply --repo <repository> --base upstream/develop
```

Use --dry-run for a proposed diff. The script updates only its managed block in
the active root AGENTS.override.md or AGENTS.md, and creates the profile only
when absent. It rejects ignored/external skill copies and unsafe workspaces.
An explicit base must match an existing recorded base. Existing profiles are
preserved even when incomplete.

Use monomind-onboarding when installed; otherwise inspect only the requested
boundary's missing fields and conduct the same evidence/approval loop here.
Verified mechanical facts cite evidence. Owner/lead policy and not-applicable
decisions require approval; retain unresolved values until then.

## Readiness and schema upgrades

```bash
python3 <skill-dir>/scripts/adopt.py check --repo <repository>
python3 <skill-dir>/scripts/adopt.py check --gate build --repo <repository>
python3 <skill-dir>/scripts/adopt.py check --gate integration --repo <repository>
python3 <skill-dir>/scripts/adopt.py check --gate release --repo <repository>
```

Choose **one** gate for the requested boundary. A gated check includes structural
validation and lower boundaries. The ungated command is only for a structural
audit; it warns about unresolved policy without claiming readiness.

Build permits implementation; Integration permits integration/merge under the
recorded authority; Release additionally requires deployment and recovery
policy. Passing a gate never authorizes an action the user did not request.

Required fields and supported versions live in scripts/policy.py. Documentation
bullets and optional links are not a schema. New profiles declare version 2;
unversioned/version-1 profiles remain readable without adding informational
fields. For upgrades, update the project-local skill and plugin together, review
the managed-block diff using apply --dry-run, then apply in the task worktree.
Do not replace the existing profile: resolve required missing fields reported
by the selected gate while preserving approvals. Unknown schema versions fail
with a compatibility message.

## Optional onboarding reminder

The trusted plugin SessionStart hook reads policy using its own packaged shared
module. It never executes Python from the target repository. A profile or active
managed instruction block opts the repository in; otherwise it remains silent.

Optional .monomind/onboarding.json settings:

```json
{"enabled": true, "gate": "integration"}
```

The default reminder boundary is Build. Set enabled to false to dismiss reminders.
This does not bypass any gate. Incomplete Release policy does not nag a Build
session. An unchanged unresolved required field can still prompt on a later
session; this is stateless and creates no hidden cache files.

Installation cannot start an agent turn or supply policy approval. Hook trust,
CI, branch protection, and agent instructions remain separate enforcement layers.
After adoption, start a new agent run to load the persistent instructions.
