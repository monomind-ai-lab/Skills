# Curating upstream changes

Use two maintenance lanes. A freshness check is read-only and does not authorize
either lane to update. Do not schedule checks, install packages, enable hooks,
or publish changes unless the user requests those actions.

| Lane | Integrations | Adoption unit |
| --- | --- | --- |
| Selective curation | Monomind phase skills, Monolayer, First Mate reference | A justified idea or reviewed wrapper-contract change |
| Intact optional distribution | EGM | One complete upstream revision, without local patches |

Updating the `monomind-egm` router does not update an installed EGM plugin.
Track the catalog snapshot, exported bundle, and actually installed plugin
revision separately; deployment of a newly curated bundle is an explicitly
authorized installation step.

## Discover and triage

1. Resolve the manifest's exact tracking ref and record its immutable candidate
   SHA. Compare against the last reviewed revision, not an old full-audit pin.
   A changed head is a review signal; establish ancestry before calling it an
   advance. A failed check means unknown freshness.
2. Read release notes and the complete changed-path list. Classify changes as
   licensing/security, behavioral workflow, host compatibility, packaging,
   documentation, or unrelated runtime internals. Prioritize changes affecting
   trust boundaries and actual user behavior over version numbers.
3. Record **adopt**, **defer**, or **reject**, with evidence and impact. Keep
   the existing pin for deferred/rejected candidates; do not mark them audited
   merely to silence freshness reports. Report their disposition separately.

The existing selected-file report is useful for wrapper triage:

```bash
python3 scripts/review_upstream_skill.py upstreams/monolayer.json
python3 scripts/review_upstream_skill.py upstreams/egm.json
```

The EGM watch list is only an early warning. That report neither inventories
new/deleted paths nor establishes complete distribution compatibility. A clean
selected-file report must never be used as approval to advance EGM's pin.

## Selective curation lane

Keep original Monomind expression, standalone packaging, and authority rules.
Apply each integration's manifest rules, including Monolayer branding, before
advancing its reviewed pin. Do not import Firstmate's distribution into the
default catalog or copy unlicensed/PolyForm source. Update affected skills,
evals, notices, and curation decisions together. Full audits and focused reviews
remain separately identified.

## EGM distribution lane

1. Start an owned task worktree from the approved base. Obtain the explicitly
   selected candidate into temporary storage and inspect the whole old/new Git
   tree diff, including new, removed, hidden, binary, and executable files.
   Review personas, shared resources, native adapters, manifests, hooks, tests,
   and licenses. Do not execute fetched code during discovery.
2. Review the candidate's fit with user choice, read-only reviewer boundaries,
   fresh-context support, external effects, and artifact handling. Preserve EGM
   branding and process. If a change conflicts with Monomind's integration
   boundary, defer the revision or propose a separately approved adapter change;
   do not silently patch files in the upstream snapshot.
3. Import **all tracked files from the exact commit**, retaining their paths,
   bytes, and executable modes, without `.git`, dependencies, or generated
   output. Remove files no longer tracked by that candidate. Do not fetch and
   copy a moving branch at different moments.
4. Rebuild `upstreams/egm.json`'s inventory from the candidate's Git tree:
   `git ls-tree -rz <candidate>` supplies each path, mode, and blob ID;
   `git rev-parse <candidate>^{tree}` supplies the root tree. Update the audited
   revision, date, plugin version, and review scope together. Recheck third-party
   components such as fonts and retain supplemental license provenance.
5. Run `python3 scripts/egm_distribution.py verify`, distribution failure tests,
   the catalog validator, skill validators for changed skills, and the repository
   suite. Run EGM's documented offline tests in a temporary copy using existing
   test dependencies. Do not modify the snapshot to make tests pass. Native
   plugin and fresh-context workflow probes are separate, explicitly authorized
   tests; record untested hosts and inherited upstream failures honestly.
6. Review the complete diff and update the distribution guide, relevant evals,
   curation record, and notices. Advance the pin only in the same reviewed change
   as the complete snapshot. Committing, pushing, publishing, and installation
   remain separately authorized delivery actions.

Record each decision with source, old/candidate SHA, changed behavior, adopted
scope, checks actually run, host limitations, and rollback. Rollback restores
the prior snapshot **and** its manifest/integration guidance as one change;
already installed plugins require a separate authorized rollback. Do not rewrite
user design documents or project state as part of distribution rollback.

## Initial follow-up priorities

The October 26 review identified Monolayer's artifact-boundary and input fixes
as the first focused re-audit, followed by Matt's test-evidence guidance and
Addy's validation/documentation improvements. Michael's changes remain subject
to its existing license boundary. Firstmate warrants a separate distribution
review rather than importing its fleet internals. These are proposed curation
tasks, not changes bundled with EGM adoption.
