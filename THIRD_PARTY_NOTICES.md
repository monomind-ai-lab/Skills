# Third-party notices

This project includes original Monomind curation and an explicitly optional EGM distribution. Original skills do not include upstream source trees; the EGM exception below preserves its complete pinned snapshot without Git history. Licensed influences and the unlicensed design reference are documented here; third-party material retains its own license.

## google/elephant-goldfish-model — optional distribution

- Source: <https://github.com/google/elephant-goldfish-model>
- Revision: `3d0b34821ce88ad328b0c9bf0e06d7eb5f1cd669`, plugin version `0.1.0`
- Copyright 2026 Google LLC and the upstream authors as identified in source
- License: Apache License, Version 2.0, except third-party components under their own terms
- Location: `distributions/egm/upstream/`

The complete tracked snapshot is redistributed unchanged, including existing
copyright and attribution notices. Its full license is preserved at
[`distributions/egm/upstream/LICENSE`](distributions/egm/upstream/LICENSE).
The root MIT license does not relicense this distribution. Monomind integration
guidance lives outside the snapshot. EGM is not an officially supported Google
product, and redistribution does not imply endorsement.

The upstream site identifies its Google Sans Flex and Google Sans Code fonts
as SIL Open Font License 1.1 material. Supplementary license copies are supplied
beside the unchanged snapshot:

- Copyright 2015 The Google Sans Flex Authors:
  [`googlesansflex-OFL.txt`](distributions/egm/licenses/googlesansflex-OFL.txt)
- Copyright 2025 The Google Sans Code Project Authors:
  [`googlesanscode-OFL.txt`](distributions/egm/licenses/googlesanscode-OFL.txt)

These copies retain the copyright and license text with normalized line endings.
Their official source URLs, retrieval date, source digests, and distributed-file
digests are recorded in `upstreams/egm.json`. Font files are not relicensed under
Apache-2.0 or MIT. Site package dependencies are listed upstream but no installed
dependency tree or compiled site is included.

## addyosmani/agent-skills

- Source: <https://github.com/addyosmani/agent-skills>
- Revision inspected: `d2c37ef6225dd8726cdd369a8030307f48592d26`
- Copyright (c) 2025 Addy Osmani
- License: MIT

```text
MIT License

Copyright (c) 2025 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## mattpocock/skills

- Source: <https://github.com/mattpocock/skills>
- Revision inspected: `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`
- Copyright (c) 2026 Matt Pocock
- License: MIT

```text
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## michaelshimeles/skills

- Source: <https://github.com/michaelshimeles/skills>
- Revision inspected: `5d403ea66775c04df222a1e9b302ef64ae45c712`
- Repository-wide license: none found at the inspected revision

This repository was consulted only for design ideas: its `AGENTS.md` four-beat task workflow, multi-agent isolation, revision-bound evidence, action/service separation, and PR completion discipline. No source file, recorder, fixture, or upstream wording from its unlicensed root material is included here.

Its `before-and-after` subtree is not copied or redistributed. The original `monomind-before-after` instructions optionally invoke the external [`@vercel/before-and-after`](https://www.npmjs.com/package/@vercel/before-and-after) package, which remains copyright (c) 2026 James Clements and licensed under [PolyForm Shield 1.0.0](https://polyformproject.org/licenses/shield/1.0.0). Users are responsible for complying with that external license. Its Greptile subtrees were MIT licensed but were intentionally excluded as vendor-specific.

## kunchenguid/firstmate

- Source: <https://github.com/kunchenguid/firstmate>
- Revision inspected: `795e5e4aacdf120908224617cfcc4dd1b76e0d37`
- Copyright (c) 2026 Kun Chen
- License: MIT

Firstmate was used as an orchestration and agent-distro design reference. The
Monomind `firstmate` skill is original catalog material refined from a
user-provided role brief. No upstream script, hook, internal skill, state tree,
or Git history is included.

## kunchenguid/lavish-axi

- Source: <https://github.com/kunchenguid/lavish-axi>
- Last full audit: `4413dcc8eff35cdc659e2035b94194d3c9be55fa` / `lavish-axi@0.1.71`
- Focused reviewed pin: `a2a199cd2275ab4d5cea1b94d42e2479bda36321` / `lavish-axi@0.1.80` (2026-09-30)
- Copyright (c) 2026 Kun Chen
- License: MIT

The original Monolayer skill integrates with the external `lavish-axi` package;
it does not vendor the package, its generated bundles, fonts, source tree, or Git
history. The package's own `THIRD-PARTY-NOTICES.md` governs software bundled in
its published distribution. Users who authorize package execution or hosted
sharing remain responsible for the external package and service terms.
The upstream `THIRD-PARTY-NOTICES.md` content did not change between the two
reviewed pins; this update records the newer external package version without
importing its software or notice text.
