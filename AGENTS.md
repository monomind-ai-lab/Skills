# Repository instructions

This repository is a curated Agent Skills collection, not a mirror of any upstream source.

- Keep every `skills/<name>/SKILL.md` usable when installed alone. Do not add pointers to shared root references required at runtime.
- Keep descriptions trigger-focused and distinct. Add or update the matching `evals/cases/<name>.json` whenever a description or workflow changes.
- Preserve explicit authority: skills may diagnose, review, plan, or assess readiness without inferring permission to edit, publish, commit, push, message, install, or deploy.
- Use project evidence rather than embedding universal commands, branches, file counts, timing, or rollout thresholds.
- Do not vendor upstream repositories or copy unlicensed/PolyForm material. Record new source influence in `docs/curation.md` and `THIRD_PARTY_NOTICES.md` when required.
- Use `apply_patch` for edits and run `python3 scripts/validate_catalog.py` plus the skill-creator validator for each changed skill before handoff.
- Keep changes scoped and inspect the diff. Do not commit unless the user asks.
