# Monomind Software Factory Skills

A curated, original collection for moving software work from intent to a safe
release. This repository is a new composition, not a fork or source mirror. It
combines durable ideas from three public skill collections and reconciles them
with Monomind's authority, isolation, architecture, and evidence model.

```text
INSTALL → ONBOARD → INTAKE → SPEC → PLAN → BUILD → EVIDENCE → REVIEW → RELEASE
                                  ↕         ↘
                                DESIGN      DEBUG

HANDOFF captures durable continuation state at any phase.
WORKFLOW conducts a complete code task as ISOLATE → BUILD → PROVE → SHIP.
```

## Start here: install, onboard, use

Installation, structural adoption, and readiness are separate states:

Version 0.2 uses one versioned policy parser for the workflow and trusted plugin
hook. Build, Integration, and Release have separate gates. Informational links
are not required policy, and unversioned legacy profiles remain supported.

- **Install** makes skill names and descriptions available to the agent.
- **Adopt** writes the small always-on repository instruction block and creates
  the `.monomind/workflow.md` scaffold without replacing existing content.
- **Onboard** discovers project facts, asks the repo owner or project lead for
  policy decisions, writes approved answers, and certifies the requested readiness gate.

Skill installation alone does **not** make cross-cutting principles mandatory,
and the presence of `.monomind/workflow.md` does **not** make a repository ready.

### 1. Create the adoption worktree

Factory adoption is a repository change. Use a task-owned linked worktree from
the approved authoritative base; reuse the harness-created task worktree when
available. These examples use the bootstrap default `origin/main`. For a different
approved base, create the worktree from that ref and supply `--base upstream/develop`
on initial `adopt.py apply`; the script records it and honors it thereafter.

```bash
git fetch origin
git worktree add ../my-repo-adopt-monomind \
  -b chore/adopt-monomind origin/main
cd ../my-repo-adopt-monomind
```

### 2. Install the skills

The commands below use the open [`skills` CLI](https://github.com/vercel-labs/skills)
through `npx`, so Git, Node.js, and `npx` must be available.

List the catalog without installing anything:

```bash
npx skills add monomind-ai-lab/Skills --list
```

Install the complete collection into the current repository for Codex:

```bash
npx skills add monomind-ai-lab/Skills \
  --skill '*' --agent codex --copy -y
```

This places repo-scoped Codex skills under `.agents/skills/`. `--copy` makes the
checked-in project self-contained instead of depending on a local symlink target.
Replace `codex` with another [supported agent identifier](https://github.com/vercel-labs/skills#supported-agents)
when needed, and use that host's native explicit-invocation syntax. The `$skill`
examples below are Codex syntax.

For a smaller installation, include `monomind-workflow` whenever the repository
will perform implementation work and `monomind-onboarding` whenever the profile
must be created, completed, or refreshed:

```bash
npx skills add monomind-ai-lab/Skills \
  --skill monomind-onboarding \
  --skill monomind-workflow \
  --skill monomind-build \
  --skill monomind-evidence \
  --skill monomind-before-after \
  --agent codex --copy -y
```

A review-only repository can install only `monomind-review`. That skill governs
reviews when selected, but it does not install the factory-wide implementation
contract.

Use `-g` only for personal experimentation across repositories. A global skill
is available to that user; it does not add team policy to any repository.

#### Recommended Codex first-run activation

For the requested first-run onboarding experience, install the repository as a
Codex plugin. Add its marketplace:

```bash
codex plugin marketplace add monomind-ai-lab/Skills --ref main
```

Open `/plugins`, select **Monomind AI Lab**, and install **Monomind Software
Factory**. Then open `/hooks`, review the bundled `SessionStart` definition, and
trust it if it matches your policy. Start a new Codex task inside the target Git
repository.

This is first-session onboarding after installation, not an installer callback.
Codex skills do not execute while they are installed, hooks cannot open a chat
or answer policy questions, and non-managed plugin hooks are skipped until the
user trusts their exact definition. On `startup`, `resume`, or `clear`, the hook
checks the current Git root only for opted-in repositories (a profile, active
managed policy, or `.monomind/onboarding.json` with `enabled: true`). It defaults
to the Build boundary and is silent when that boundary is complete. Select
`gate: "integration"` or `"release"` in that settings file to change the reminder
boundary; set `enabled: false` to dismiss reminders without bypassing gates. The agent inspects and begins asking the
policy questions on the first user turn in that repository; installation itself
does not create a background conversation. See OpenAI's official
[plugin packaging](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks)
and [hooks](https://learn.chatgpt.com/docs/hooks#sessionstart) documentation.

The plugin makes the catalog and first-run nudge available to that Codex user.
Keep the project-local `--copy` installation above when the policy and skills
must travel with the repository for teammates and other harnesses.

### 3. Adopt and onboard the persistent workflow

Start a new Codex task so it discovers the installed skills; if they still do
not appear, restart Codex. Then invoke the onboarding agent explicitly (the
trusted plugin hook supplies this route automatically when needed):

```text
$monomind-onboarding Onboard this repository for the Monomind software factory. Discover project facts first, ask me only for policy decisions, and write .monomind/workflow.md.
```

The onboarding agent uses the workflow's bundled adoption script to:

- refuse setup on `main`, the configured base branch, detached HEAD, a primary
  checkout, or a branch not based on the available approved base;
- preserve existing instructions and add or refresh one managed block in the
  active root `AGENTS.md` or `AGENTS.override.md`;
- create `.monomind/workflow.md` only when it does not exist; and
- check that the project-local workflow skill, policy block, profile, and
  configured remote remain present;
- inspect repository-native commands and policy evidence before asking; and
- interview the authorized repo owner/project lead, write approved answers, and
  run readiness gates.

Choose the single gate for your requested boundary; a gated check already
includes structural validation and lower-boundary requirements. The following
commands illustrate the available checks, not a mandatory sequence:

```bash
python3 .agents/skills/monomind-workflow/scripts/adopt.py apply --repo .
# Run $monomind-onboarding to resolve project facts and policy decisions.
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --gate build --repo .
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --gate integration --repo .
# Use --gate release instead when deployment/migration is the requested boundary.
```

Every `UNRESOLVED` value must be defined separately for this repository. Agents
may fill mechanically verified facts with an evidence pointer. Integration
strategy, authority, required gates, release controls, continuity ownership
(see [project-context](https://github.com/monomind-ai-lab/project-context) and
[project-hub](https://github.com/monomind-ai-lab/project-hub)), and
other policy choices must be approved by the repository owner, project lead, or
an explicitly named delegate. If a field truly does not apply, record
`NOT_APPLICABLE — <specific approved or evidenced reason>`; a bare `N/A` does
not pass any readiness gate. Resolve fields for the requested boundary only.

The interview follows a reviewable loop:

1. Inspect instructions, remotes, manifests, CI/CD, ownership, releases,
   resources, and context/handoff sources (see
   [project-context](https://github.com/monomind-ai-lab/project-context) and
   [project-hub](https://github.com/monomind-ai-lab/project-hub)).
2. Show the owner or lead the verified facts and their evidence.
3. Ask grouped questions only for policy that evidence cannot establish.
4. Write each confirmed value with an evidence or approval reference and date.
5. Run the gates and report remaining fields and their decision owner.

| Status | Meaning |
| --- | --- |
| Structurally adopted | Skill, managed instruction block, profile, and configured remote are present; `UNRESOLVED` may remain and is reported |
| Build-ready | Ownership, task/worktree model, naming, setup, focused/regression tests, architecture, shared resources, continuity, and mutation authority are resolved |
| Integration-ready | Build-ready plus integration, check, CI/review, evidence, safety, context, and merge policy is resolved |
| Release-ready | Integration-ready plus deployment, release, observation, and recovery policy is resolved |

Build agents stop when the Build gate fails. Integration and merge use the
Integration gate; executing deployment or migration uses Release. A
read-only assessment may identify gaps without crossing those mutation gates.

Review the resulting diff before committing. Installation and adoption do not
grant permission to commit, push, open a pull request, or merge. Codex
[discovers repository instructions once per run](https://developers.openai.com/codex/agent-configuration/agents-md#how-codex-discovers-guidance),
so start a new task after adoption to exercise the persistent policy.

### 4. Use it after the relevant gate passes

In that new task, speak normally for a new implementation request:

```text
Add team invitations and take the change through a PR-ready handoff.
```

The adopted `AGENTS.md` rule requires the Build-ready gate and
`$monomind-workflow` before editing, even if implicit skill matching would
otherwise miss them. The workflow conducts Isolate → Build → Prove → Ship,
requires Integration-ready before integration and Release-ready before deployment, and stops Ship at the
furthest action the user or project has authorized.

For an already-isolated single phase, invoke the narrower skill directly:

```text
$monomind-build Implement the approved invitation-acceptance slice in this task worktree.
```

## How triggering actually works

Skills are not hooks. Codex uses [progressive disclosure](https://developers.openai.com/codex/skills):

1. It initially sees each installed skill's `name` and `description`.
2. It loads the full `SKILL.md` only after selecting that skill.
3. It reads references or runs bundled scripts only when the selected workflow
   needs them.

There are four activation paths:

| Path | What causes it | Reliability and scope |
| --- | --- | --- |
| Explicit | Mention `$monomind-build`, or use `/skills`/`$` selection in Codex | Forces that skill for the current task |
| Implicit | The request matches a skill's frontmatter `description` | Convenient routing, but still a model decision |
| Persistent policy | The adopted root `AGENTS.md` contains mandatory if/then rules | Loaded before repository work and applies across tasks |
| Plugin first-session nudge | A trusted `SessionStart` hook sees an opted-in repository missing policy for its selected boundary | Adds developer context that routes the agent to onboarding; cannot start a turn or decide policy |

The skills-CLI path does not install a lifecycle hook. The optional Codex plugin
bundles the first-session nudge, but it remains a separate, host-specific layer
that Codex skips until the user reviews and trusts it. The hook contributes
context; skill selection and the interactive policy interview still happen in
the agent task.

For stronger enforcement, use the layers together:

| Layer | What it reinforces | What it cannot guarantee |
| --- | --- | --- |
| `monomind-onboarding` | Evidence discovery, owner/lead interview, profile writing, and readiness certification | That its proposed policy is approved without an authorized human answer |
| Skill body | Correct procedure while that skill is active | That the skill will always be selected |
| Trusted plugin `SessionStart` hook | Routing for opted-in repositories missing policy at the selected boundary | An install-time conversation, repository writes, or policy approval |
| Adopted `AGENTS.md` | Mandatory onboarding/readiness routing, worktree rule, architecture ownership, and UI proof | Compliance by tools that ignore repository instructions |
| `adopt.py check` | Detects missing or drifted policy, profile, project skill, and remote configuration | Readiness while reported values remain unresolved |
| `adopt.py check --gate build/integration/release` | Fails when fields required at that boundary are missing, unresolved, empty, or bare not-applicable | Whether an apparently resolved value was approved honestly |
| `adopt.py preflight` | Verifies the current branch is an approved-base linked task worktree | Future pushes, reviews, or merges |
| CI and branch protection | Required checks and no direct push to protected `main` | Local edits made before CI starts |

Wire this command into CI when policy drift should fail a build:

```bash
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --gate integration --repo .
# Use --gate release instead when deployment/migration is the requested boundary.
```

Use branch protection for a server-side no-direct-push rule. Keep any additional
Codex `PreToolUse` enforcement explicit, reviewable, and scoped; the bundled
hook is an onboarding nudge, not a general command interceptor.

## Which skill should I use?

Natural-language requests can trigger these implicitly. The last column shows
the explicit form when deterministic selection matters.

| Skill | Reach for it when | Explicit example |
| --- | --- | --- |
| [`monomind-onboarding`](skills/monomind-onboarding/SKILL.md) | The profile is absent/incomplete, owner or lead policies need an interview, or readiness must be certified | `$monomind-onboarding Complete this repo's policy profile with me.` |
| [`monomind-workflow`](skills/monomind-workflow/SKILL.md) | Structurally adopting the factory, starting a ready code-changing task, coordinating concurrent work, or taking work end to end | `$monomind-workflow Take this issue through a PR-ready handoff.` |
| [`monomind-intake`](skills/monomind-intake/SKILL.md) | The user, outcome, success signal, constraint, or non-goals are unclear | `$monomind-intake Clarify this feature request.` |
| [`monomind-spec`](skills/monomind-spec/SKILL.md) | Clear intent needs a living behavioral and operational contract | `$monomind-spec Turn the approved intent into a spec.` |
| [`monomind-plan`](skills/monomind-plan/SKILL.md) | A spec needs ordered vertical tasks, acceptance criteria, and blocking edges | `$monomind-plan Break this spec into executable slices.` |
| [`monomind-design`](skills/monomind-design/SKILL.md) | Module seams, ownership, or policy/mechanics boundaries need work | `$monomind-design Design the module boundary first.` |
| [`monomind-build`](skills/monomind-build/SKILL.md) | An approved slice is already isolated and ready to implement | `$monomind-build Implement the next approved slice.` |
| [`monomind-debug`](skills/monomind-debug/SKILL.md) | A failure or regression needs a reproducible root cause | `$monomind-debug Diagnose this intermittent failure.` |
| [`monomind-evidence`](skills/monomind-evidence/SKILL.md) | Tests alone cannot prove a runtime, migration, performance, or visible claim | `$monomind-evidence Capture revision-bound proof.` |
| [`monomind-before-after`](skills/monomind-before-after/SKILL.md) | A UI change needs a controlled visual pair and PR-ready Markdown | `$monomind-before-after Compare production and preview.` |
| [`monomind-review`](skills/monomind-review/SKILL.md) | A diff or pull request needs spec-fidelity and engineering-quality review | `$monomind-review Review this branch against its spec.` |
| [`monomind-release`](skills/monomind-release/SKILL.md) | Work approaches a live rollout, migration, or launch gate | `$monomind-release Assess release readiness.` |
| [`monomind-handoff`](skills/monomind-handoff/SKILL.md) | Another session, agent, or human must continue without rereading the transcript | `$monomind-handoff Prepare continuation state.` |

Routing rule: a missing/incomplete profile or failed readiness gate enters
through `monomind-onboarding`; a ready newly started code-changing task enters
through `monomind-workflow`; read-only work and an already-isolated single phase
use the smallest relevant phase skill. Installing `monomind-build` alone gives
that skill its own isolation and architecture checks when it runs, but only
adoption makes those principles persistent across repository tasks.

## Repository policy principles

| Area | Monomind policy posture |
| --- | --- |
| Collaboration | One named task owner, branch, and worktree; coordinate overlap and shared resources; never alter another owner's unknown work |
| Integration | Base work on the approved authoritative branch, protect that base, define one project integration strategy, and keep commit/push/PR/reply/merge authority separate |
| Testing | Use exact repository-native commands, prove behavior through public seams, retain failing-before evidence when feasible, and never weaken gates to reach green |
| CI/CD | Declare required gates, triggers, reviewers, blocking findings, and override authority; enforce server-side invariants in reviewed configuration |
| Release | Separate assessment from live execution; name artifact, environment, owner, approval, signals, observation, migration, rollback, and cleanup |
| Context and continuity | Keep durable truth in repository-owned specs, decisions, task/context records, and evidence; update before transfer/compaction and verify freshness on resume. Optional context tools include [project-context](https://github.com/monomind-ai-lab/project-context) (repo-level) with the org-level hub in [project-hub](https://github.com/monomind-ai-lab/project-hub) |

The full interview guidance and rationale live in
[`policy-principles.md`](skills/monomind-onboarding/references/policy-principles.md).

## Curation principles

- **Isolate implementation:** every implementation task starts from
  the approved base in an owned linked worktree; never build on the base or another
  agent's state.
- **Actions own why/when; services own reusable how:** side-effecting boundaries
  retain policy while reusable capabilities expose explicit inputs, structured
  returns, and typed failures.
- **Behavior over ceremony:** keep gates that prevent rework while commits,
  publication, review replies, and merge remain explicit delivery actions.
- **Project evidence over remembered defaults:** discover commands, versions,
  conventions, baselines, and current state from the active repository.
- **Public seams over internals:** specs, tests, and reviews describe observable
  behavior through stable interfaces.
- **Thin vertical slices:** deliver complete paths; use expand–migrate–contract
  only for genuinely wide compatibility changes.
- **Proof bound to a revision:** every runtime claim identifies the code and
  environment actually tested.
- **Standalone packaging:** each phase skill remains usable when installed alone.

The audit trail, source revisions, license treatment, adopted ideas, exclusions,
and conflict resolutions are in [`docs/curation.md`](docs/curation.md). The
Michael Shimeles `AGENTS.md` benchmark is reviewed in
[`docs/benchmarks/michaelshimeles-agents.md`](docs/benchmarks/michaelshimeles-agents.md).
Full notices are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Update and validate

Update project-installed skills with the skills CLI, then reapply the managed
policy in case its contract changed:

```bash
npx skills update -p -y
python3 .agents/skills/monomind-workflow/scripts/adopt.py apply --repo .
# Use $monomind-onboarding only for required missing fields at the requested boundary.
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --gate build --repo .
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --gate integration --repo .
# Use --gate release instead when deployment/migration is the requested boundary.
```

Contributors to this catalog should run:

```bash
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests -v
```

The catalog validator checks skill structure, UI metadata, eval coverage,
trigger routing, negative-owner routing, and description collisions. Behavioral
scenarios live in `evals/cases/`. Real paired agent runs (quality, clarification,
tool calls, reported tokens) are documented in [evals/README.md](evals/README.md).

## License

New Monomind material is MIT licensed. Upstream license and provenance details
are preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). No upstream
Git history, source tree, recorder, Greptile integration, or PolyForm-licensed
utility is vendored; `monomind-before-after` invokes the external package under
its own license when authorized.
