# Monomind Software Factory Skills

A curated, original skill collection for moving software work from intent to a safe release. This repository is a new composition, not a fork or source mirror. It combines durable ideas from three public skill collections, reconciles their conflicts with Monomind's authority and evidence model, and keeps each installed skill standalone.

```text
INTAKE → SPEC → PLAN → BUILD → EVIDENCE → REVIEW → RELEASE
                    ↕         ↘
                  DESIGN      DEBUG

HANDOFF can capture durable continuation state at any phase.
```

## Catalog

| Skill | Reach for it when |
| --- | --- |
| [`monomind-intake`](skills/monomind-intake/SKILL.md) | The outcome, user, success signal, constraint, or non-goals are unclear |
| [`monomind-spec`](skills/monomind-spec/SKILL.md) | Clear intent needs a living behavioral and operational contract |
| [`monomind-plan`](skills/monomind-plan/SKILL.md) | A spec needs vertical tasks, acceptance criteria, and blocking edges |
| [`monomind-design`](skills/monomind-design/SKILL.md) | Module seams, ownership, or policy/mechanics boundaries need work |
| [`monomind-build`](skills/monomind-build/SKILL.md) | An approved task should be implemented in thin verified slices |
| [`monomind-debug`](skills/monomind-debug/SKILL.md) | A failure or regression needs a reproducible root cause |
| [`monomind-evidence`](skills/monomind-evidence/SKILL.md) | Tests alone cannot prove a visual, runtime, migration, or performance claim |
| [`monomind-review`](skills/monomind-review/SKILL.md) | A change needs spec-fidelity and engineering-quality review |
| [`monomind-release`](skills/monomind-release/SKILL.md) | Work approaches a live rollout, migration, or launch gate |
| [`monomind-handoff`](skills/monomind-handoff/SKILL.md) | Another session, agent, or human must continue without rereading the transcript |

Skills select independently from their descriptions. There is deliberately no broad always-on router: Monomind loads only the smallest relevant workflow.

## Curation principles

- **Behavior over ceremony:** keep gates that prevent rework; remove universal meetings, commits, worktrees, and tracker mutations.
- **Project evidence over remembered defaults:** discover commands, versions, conventions, baselines, and current state from the active repository.
- **Public seams over internals:** specs, tests, and reviews describe observable behavior through stable interfaces.
- **Thin vertical slices:** deliver complete paths; use expand–migrate–contract only for genuinely wide compatibility changes.
- **Proof bound to a revision:** every runtime claim identifies the code and environment actually tested.
- **Authority stays explicit:** review does not authorize edits, readiness does not authorize deployment, and local evidence does not authorize publishing.
- **Standalone packaging:** no skill depends on a repository-level checklist that disappears when installed alone.

The audit trail, source revisions, license treatment, adopted ideas, exclusions, and conflict resolutions are in [`docs/curation.md`](docs/curation.md). Full notices are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Use and validate

Install only the folders needed by the target agent, or expose this repository's `skills/` directory as a collection. Each skill includes Codex UI metadata under `agents/openai.yaml` but otherwise uses the portable `SKILL.md` format.

Run the deterministic catalog checks before accepting a change:

```bash
python3 scripts/validate_catalog.py
```

The validator checks skill structure, UI metadata, eval coverage, trigger routing, negative-owner routing, and description collisions. Behavioral scenarios live in `evals/cases/` for independent forward-testing by an agent harness.

## License

New Monomind material is MIT licensed. Upstream license and provenance details are preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). No upstream Git history, vendored source tree, recorder, Greptile integration, or PolyForm-licensed utility is included.
