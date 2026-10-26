# Optional EGM distribution

Choose EGM when a design benefits from deep-context drafting followed by
fresh-context, independent spec review. Monomind's ordinary workflow remains
the default. Agents may explain why EGM fits a task; only the user selects it.

This directory contains the complete, unchanged source snapshot of
[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)
at `3d0b34821ce88ad328b0c9bf0e06d7eb5f1cd669`, plugin version `0.1.0`.
All tracked files, including dotfiles, tests, documentation, and site assets,
are retained. Git history, installed dependencies, and generated files are not
part of the snapshot. The canonical revision, Git tree, file inventory, and
curation rules are in the catalog's `upstreams/egm.json`, copied to
`UPSTREAM.json` at the bundle root on export.

## Choose and use

```text
$monomind-egm Compare EGM with the normal Monomind approach for this migration.
$monomind-egm Use EGM for this feature's design and spec review.
```

The normal Monomind plugin discovers only `skills/`. It exposes the small
router, not EGM's seven runtime skills. Installing the router alone does not
install EGM or require this repository to exist beside it. Do not use recursive
full-depth discovery to install individual skills from `upstream/`: those skills
depend on their shared plugin resources.

For an authorized local export, run from a complete catalog checkout:

```bash
python3 scripts/egm_distribution.py verify
python3 scripts/egm_distribution.py export /path/outside/catalog/egm-bundle
```

The exporter refuses an existing destination or a path within this checkout.
It verifies the full inventory first, then copies this distribution, its
supplemental font licenses, and the provenance manifest. It does not install a
plugin, contact the network, or execute any upstream code. The exported plugin
root is `/path/outside/catalog/egm-bundle/upstream/`.

For Codex clients whose `plugin marketplace add --help` supports local paths,
the explicit installation steps are:

```bash
codex plugin marketplace add /path/outside/catalog/egm-bundle/upstream
codex plugin add egm@egm
```

These commands mutate host configuration and install the plugin; run them only
when installation is requested. The bundled marketplace resolves EGM from its
local `./` source. If an `egm` marketplace already exists, inspect its source
and obtain a choice before replacing it. The import's checks verified the CLI
help and bundled paths, but did not execute installation on a live account.

With a host that supports selecting a complete local plugin directory, select
that root through the host's supported interface. Otherwise use EGM's own
[host guides](upstream/docs/harnesses.md) and native installation mechanism,
with separate installation authority. Installing directly from Google's moving
repository may select a different revision from this pinned distribution;
record the actual installed revision. Do not claim pinned execution in that
case. Start a fresh session when the host requires it.

After selection, follow the bundled [README](upstream/README.md) and relevant
host adapter. EGM keeps its own brainstorm, draft, review, and resolution
process. An approved design can feed Monomind's implementation workflow; EGM
does not bypass the consuming project's worktree, evidence, or delivery rules.
Its bootstrap and drift tools are available when separately requested. Neither
the snapshot nor the router enables hooks, loads conversation history, or
starts background agents at ordinary startup.

## Licensing and verification

EGM material remains under its [Apache-2.0 license](upstream/LICENSE), with
upstream copyrights retained. The site fonts retain SIL OFL-1.1 licensing;
supplemental license copies live in `licenses/`. Monomind's root MIT license
does not relicense these materials. Monomind's integration guidance is original
MIT material. This is not an officially supported Google product.

`verify` checks the complete file set, bytes, executable bits, reconstructed
Git tree, supplemental licenses, and plugin/resource layout. It rejects extra
files and symlinks throughout the exported bundle, including its guides, so
unrelated local files cannot enter an export. It does not prove
live model execution, reviewer isolation, or every host's plugin discovery.
Upstream's [test record](upstream/TESTING.md) retains its own scope and limits.

Run catalog tests separately from upstream's documented offline tests. Live
tests require authenticated clients and model usage; run them only with that
authority. Keep test caches outside the immutable snapshot.

See [upstream curation](https://github.com/monomind-ai-lab/Skills/blob/main/docs/upstream-curation.md) for updates, rejection,
rollback, and the distinction between selective wrappers and whole snapshots.
