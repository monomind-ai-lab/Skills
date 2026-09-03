# Repository instructions

This repository is a curated Agent Skills collection, not a mirror of any upstream source.

- For every newly started feature, fix, or code-changing task, use `skills/monomind-workflow/SKILL.md`: create a fresh owned worktree from `origin/main`, never implement on `main`, then cross Isolate → Build → Prove → Ship only as far as authorized. Use narrower phase skills for already-isolated or read-only work.
- Keep installation and adoption distinct in documentation: installed skill metadata is lazy; the workflow's managed `AGENTS.md` block is persistent policy; hooks, CI, and branch protection are separate opt-in enforcement layers.
- Changes to `skills/monomind-workflow/scripts/adopt.py`, its policy block, or its profile asset require `python3 -m unittest discover -s tests -v` plus the catalog validator.
- Treat every template `UNRESOLVED` value as a project-specific decision marker. Agents may establish mechanical facts, but repository policy and `NOT_APPLICABLE` decisions require approval from that target repository's owner, project lead, or explicitly named delegate.
- Keep plugin activation claims exact: installation cannot start an agent turn; the optional trusted `SessionStart` hook may only add first-session onboarding context. Changes under `.codex-plugin/`, `.agents/plugins/`, or `hooks/` require hook tests and plugin validation.
- Keep every `skills/<name>/SKILL.md` usable when installed alone. Do not add pointers to shared root references required at runtime.
- Keep descriptions trigger-focused and distinct. Add or update the matching `evals/cases/<name>.json` whenever a description or workflow changes.
- Preserve explicit authority: skills may diagnose, review, plan, or assess readiness without inferring permission to edit, publish, commit, push, message, install, or deploy.
- Use project evidence rather than embedding universal commands, branches, file counts, timing, or rollout thresholds.
- Do not vendor upstream repositories or copy unlicensed/PolyForm material. Record new source influence in `docs/curation.md` and `THIRD_PARTY_NOTICES.md` when required.
- Use `apply_patch` for edits and run `python3 scripts/validate_catalog.py` plus the skill-creator validator for each changed skill before handoff.
- Keep changes scoped and inspect the diff. Do not commit unless the user asks.
