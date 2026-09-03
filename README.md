# Monomind Software Factory Skills

A curated, original collection for moving software work from intent to a safe
release. This repository is a new composition, not a fork or source mirror. It
combines durable ideas from three public skill collections and reconciles them
with Monomind's authority, isolation, architecture, and evidence model.

```text
INTAKE → SPEC → PLAN → BUILD → EVIDENCE → REVIEW → RELEASE
                    ↕         ↘
                  DESIGN      DEBUG

HANDOFF captures durable continuation state at any phase.
WORKFLOW conducts a complete code task as ISOLATE → BUILD → PROVE → SHIP.
```

## Start here: install, adopt, use

Installing a skill and adopting the factory are separate operations:

- **Install** makes skill names and descriptions available to the agent.
- **Adopt** writes the small always-on repository policy that requires the
  workflow and records project-specific commands in `.monomind/workflow.md`.

Skill installation alone does **not** make cross-cutting principles mandatory.

### 1. Create the adoption worktree

Factory adoption is itself a code-changing task, so start from a fresh linked
worktree. If your harness already created an exclusive worktree from
`origin/main`, use it instead.

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
will perform implementation work, then add only the phase skills it needs:

```bash
npx skills add monomind-ai-lab/Skills \
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

### 3. Adopt the persistent workflow

Start a new Codex task so it discovers the installed skills; if they still do
not appear, restart Codex. Then invoke the workflow explicitly:

```text
$monomind-workflow Adopt the Monomind software factory in this repository. Preserve existing instructions, inspect project-native commands, and verify the adoption.
```

The adoption mode uses its bundled script to:

- refuse setup on `main`, detached HEAD, a primary checkout, or a branch not
  based on the available `origin/main`;
- preserve existing instructions and add or refresh one managed block in the
  active root `AGENTS.md` or `AGENTS.override.md`;
- create `.monomind/workflow.md` only when it does not exist; and
- check that the project-local workflow skill, policy block, profile, and
  `origin` configuration remain present.

The equivalent mechanical commands are:

```bash
python3 .agents/skills/monomind-workflow/scripts/adopt.py apply --repo .
# Inspect and replace verified UNRESOLVED values in .monomind/workflow.md.
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
```

Review the resulting diff before committing. Installation and adoption do not
grant permission to commit, push, open a pull request, or merge. Codex
[discovers repository instructions once per run](https://developers.openai.com/codex/agent-configuration/agents-md#how-codex-discovers-guidance),
so start a new task after adoption to exercise the persistent policy.

### 4. Use it

In that new task, speak normally for a new implementation request:

```text
Add team invitations and take the change through a PR-ready handoff.
```

The adopted `AGENTS.md` rule requires `$monomind-workflow` before editing, even
if implicit skill matching would otherwise miss it. The workflow then conducts
Isolate → Build → Prove → Ship and stops Ship at the furthest action the user or
project has authorized.

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

There are three activation paths:

| Path | What causes it | Reliability and scope |
| --- | --- | --- |
| Explicit | Mention `$monomind-build`, or use `/skills`/`$` selection in Codex | Forces that skill for the current task |
| Implicit | The request matches a skill's frontmatter `description` | Convenient routing, but still a model decision |
| Persistent policy | The adopted root `AGENTS.md` contains mandatory if/then rules | Loaded before repository work and applies across tasks |

This repository does not silently install a lifecycle hook. Codex hooks are a
separate, host-specific mechanism that must be reviewed and trusted before they
run. They are useful for deterministic local interception, but they are not the
mechanism that selects a skill. See the official [hooks documentation](https://learn.chatgpt.com/docs/hooks).

For stronger enforcement, use the layers together:

| Layer | What it reinforces | What it cannot guarantee |
| --- | --- | --- |
| Skill body | Correct procedure while that skill is active | That the skill will always be selected |
| Adopted `AGENTS.md` | Mandatory workflow routing, worktree rule, architecture ownership, and UI proof | Compliance by tools that ignore repository instructions |
| `adopt.py check` | Detects missing or drifted policy, profile, project skill, and remote configuration | Whether every implementation command happened in the right order |
| `adopt.py preflight` | Verifies the current branch is an `origin/main`-based linked task worktree | Future pushes, reviews, or merges |
| CI and branch protection | Required checks and no direct push to protected `main` | Local edits made before CI starts |

Wire this command into CI when policy drift should fail a build:

```bash
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
```

Use branch protection for a server-side no-direct-push rule. If a repository
later adds a Codex `PreToolUse` hook, keep it explicit, reviewable, and scoped;
the portable catalog deliberately does not enable one during skill installation.

## Which skill should I use?

Natural-language requests can trigger these implicitly. The last column shows
the explicit form when deterministic selection matters.

| Skill | Reach for it when | Explicit example |
| --- | --- | --- |
| [`monomind-workflow`](skills/monomind-workflow/SKILL.md) | Adopting the factory, starting any new code-changing task, coordinating concurrent work, or taking work end to end | `$monomind-workflow Take this issue through a PR-ready handoff.` |
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

Routing rule: a newly started code-changing task enters through
`monomind-workflow`; read-only work and an already-isolated single phase use the
smallest relevant phase skill. Installing `monomind-build` alone gives that
skill its own isolation and architecture checks when it runs, but only adoption
makes those principles persistent across repository tasks.

## Curation principles

- **Isolate implementation:** every implementation task starts from
  `origin/main` in a fresh owned worktree; never build on `main` or another
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
python3 .agents/skills/monomind-workflow/scripts/adopt.py check --repo .
```

Contributors to this catalog should run:

```bash
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests -v
```

The catalog validator checks skill structure, UI metadata, eval coverage,
trigger routing, negative-owner routing, and description collisions. Behavioral
scenarios live in `evals/cases/` for independent forward-testing.

## License

New Monomind material is MIT licensed. Upstream license and provenance details
are preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). No upstream
Git history, source tree, recorder, Greptile integration, or PolyForm-licensed
utility is vendored; `monomind-before-after` invokes the external package under
its own license when authorized.
