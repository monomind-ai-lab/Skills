---
name: monomind-egm
description: "Choose or use the optional Elephant-Goldfish Model (EGM) distribution for deep-context drafting and fresh-context spec stress-testing. Use when EGM is named, when comparing development approaches, or when consequential design uncertainty warrants suggesting independent Goldfish review. Routine fixes stay with the existing workflow."
---

# Monomind EGM

Route to the complete EGM distribution without translating its process into
Monomind phase skills. This standalone router contains no EGM runtime and
does not require a sibling catalog checkout to explain or select the approach.

## Suggest or select

EGM suits unresolved architecture alternatives, unfamiliar systems, or migration
designs whose assumptions deserve independent spec review. Explain the concrete
benefit and cost: fresh reviewers can expose context gaps, but the process adds
model usage, artifacts, and human review checkpoints. A suggestion is not
selection. Wait for the user to choose EGM unless they already selected it for
this task or project. Do not suggest it for routine, settled changes.

## Locate the complete distribution

Use an explicitly supplied EGM root or the host's installed plugin metadata.
In a Monomind catalog checkout, `distributions/egm/upstream/` is the pinned root;
the catalog's `scripts/egm_distribution.py verify` checks its integrity offline.
Do not assume that a globally installed router contains that checkout or search
unrelated directories for one.

If the runtime is absent, explain that the complete bundle is required and link
to the [Monomind distribution guide](https://github.com/monomind-ai-lab/Skills/blob/main/distributions/egm/README.md).
The router remains usable for approach selection. Installation or export needs
the user's authority; do not silently download EGM or install its individual
skills. A complete EGM plugin includes `skills/`, `agents/`, `resources/`,
`docs/`, native manifests, and its license.

## Run the selected approach

Read the located EGM README and the adapter for the current host, then load only
the selected EGM skill and its required resources. Preserve EGM's names,
approval gates, rubrics, and fresh-context requirements. Do not load upstream
repository-contribution instructions as policy for the user's project.

Dispatch Goldfish reviewers only within the selected workflow's authority and
the host's capabilities. Verify fresh-context support and actual reviewer
completion; isolation from the parent conversation does not isolate shared
files or memory. If unavailable, report the limitation instead of simulating
Goldfish reviewers in the author context.

EGM owns ideation, drafting, and spec review while selected. Do not interleave
Monomind intake/spec checkpoints with that same stage. An approved EGM design
can become the input to the project's implementation workflow; choosing EGM
does not waive isolation, proof, or release requirements. Bootstrap and drift
commands remain separately scoped tasks. Selection does not authorize package
installation, commits, publication, deployment, or broader filesystem access.

Finish with the chosen approach, source revision when known, artifacts,
verification gaps, and the next authorized phase. Never describe installation
or packaging checks as evidence of a completed live EGM workflow.
