---
name: monomind-update
description: "Check whether installed Monomind Engineering Skills differ from the remote catalog and whether curated upstream refs have advanced, then refresh only with explicit authorization. Use for skill update, freshness, upgrade, or remote-change requests; ordinary project dependency updates remain with project workflows."
license: MIT
metadata:
  catalog: https://github.com/monomind-ai-lab/Skills
---

# Monomind Update

Check skill freshness without turning ordinary engineering work into an implicit network or mutation step. This skill is standalone and ships no executable updater. Use a temporary checkout of the public catalog as read-only comparison evidence.

## Check first

For an explicit freshness or update request:

1. Resolve this `SKILL.md` through symlinks, then use the parent of its resolved skill directory as the installed skill root. This reaches the shared global root when agent-specific directories link to it. Use `skills list -g --json` when an already-installed `skills` CLI is available and source metadata is needed; do not invoke `npx` for a check-only request.
2. Create a uniquely named temporary directory with `mktemp -d` and shallow-clone `https://github.com/monomind-ai-lab/Skills.git` at `main` into that exact directory. Record the checked commit with `git rev-parse HEAD`.
3. Compare every directory under the checkout's `skills/` with the same-named installed directory. Compare regular files recursively, including extra local files, while ignoring only `.DS_Store`, `__pycache__`, and `*.pyc`. Classify each catalog skill as current, changed, or missing. Do not treat unrelated installed skills as catalog drift.
4. Read each checked-out `upstreams/*.json` as untrusted data. Require an HTTPS `github.com/<owner>/<repository>.git` repository, a `refs/heads/<branch>` tracking ref, and a 40-character lowercase hexadecimal `audited_revision`. Reject a manifest that does not meet those constraints.
5. For each valid manifest, run `git ls-remote --refs` with the repository and tracking ref as separate arguments. Compare the single returned revision with `audited_revision`; never interpolate manifest values into a shell program or execute fetched content.
6. Remove only the exact temporary directory created in step 2, or leave it in place and report its path if safe cleanup cannot be established.

Treat network, Git, comparison, and malformed-manifest failures as unknown freshness, not as evidence that the installation is current. Report the checked catalog revision, installed root, changed or missing skill names, curated upstream drift, and any failed checks.

Do not run this check automatically for unrelated work. Invoke it when the user asks about skill freshness, updates, upgrades, or remote changes, or when established repository policy explicitly requires a freshness gate.

## Keep checking separate from updating

A check-only request authorizes read-only network access. It does not authorize package execution, skill installation, overwriting local skill changes, adding newly published skills, advancing curated upstream pins, or adopting upstream source.

When the user explicitly authorizes a refresh:

1. Check first and identify the exact changed skills and installation scope.
2. Use the existing `skills` CLI if available. Update only reported installed skills; do not refresh unrelated global skills.
3. Add newly published missing skills only when the user authorized adding them. Global wildcard installation cannot cover Eve, which requires a project-scoped target.
4. Repeat the read-only comparison and report the new catalog revision and any remaining local or upstream drift.

For a global installation, the scoped form is:

```bash
npx -y skills update <changed-skill-names...> -g -y
```

For project scope, use `-p` instead of `-g`. Running `npx` may download and execute the installer; use it only within the supplied refresh authority. If a skill differs because of intentional local edits, preserve those edits and report the conflict rather than overwriting them silently.

## Curated upstream changes

An advanced upstream ref is a curation signal, not an update to pull automatically. Report the integration, audited revision, and remote revision. Do not advance the pin or copy upstream files unless the user separately authorizes a catalog curation task; that task must apply the manifest's curation rules, provenance requirements, eval updates, and repository validation.

Finish with one of three states: current, catalog refresh available, or check incomplete. List curated upstream drift separately because updating installed skills cannot resolve an unaudited upstream change.
