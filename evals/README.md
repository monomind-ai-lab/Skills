# Catalog evals

Each `cases/<skill-name>.json` tests two different properties:

1. **Routing:** realistic positive prompts should rank the intended skill within `top_k`; negative prompts name the skill that should outrank it.
2. **Behavior contract:** one scenario lists observable expectations for an independent agent run. These scenarios are deliberately outcome-based rather than wording snapshots.

The case shape is:

```json
{
  "skill_name": "monomind-example",
  "trigger": {
    "positive": [
      { "prompt": "A realistic request", "top_k": 1 }
    ],
    "negative": [
      { "prompt": "A request owned elsewhere", "owner": "monomind-other" }
    ]
  },
  "evals": [
    {
      "id": 1,
      "kind": "execution",
      "prompt": "A realistic task",
      "expected_output": "A concise outcome description",
      "expectations": [
        "A verifiable behavior",
        "Another verifiable behavior",
        "A completion condition"
      ]
    }
  ]
}
```

`kind` is `dialogue` when the deliverable is the conversation itself and `execution` when a forward test should run in an isolated repository. This repository validates the contracts and deterministic lexical routing locally; a model harness can execute and grade the behavioral scenarios independently.

Run:

```bash
python3 scripts/validate_catalog.py
```

## Actual paired agent runs

Latest measured pilot: [architecture changes and agent results](../docs/benchmarks/architecture-agent-evals.md).

Run the baseline and current working skills through the signed-in Codex CLI:

```bash
python3 scripts/benchmark_agents.py --baseline a00d263 \
  --model gpt-5.6-sol --effort medium --repeats 2 --jobs 2
```

This consumes model usage through the existing Codex login. It creates isolated
local Git fixtures and makes no remote Git mutations. Each arm gets the same
unversioned policy input and task. The baseline is copied from the pinned Git
revision; the candidate is snapshotted before any trial. Snapshot hashes, CLI
version, model, effort, prompts, final outputs, and JSONL events are retained
under gitignored `evals/results/agents-*/`. Jobs run with plugins/hooks/apps and
delegation disabled; explicit fixture instructions and installed skills remain
available. Therefore these trials test agent/skill behavior, not automatic
plugin activation. Hook routing is covered by unit tests.

Three scenarios exercise different claims:

- **Implementation:** slug normalization, graded by hidden public-function
  assertions, regression tests, scoped changes, and truthful completion.
- **Integration:** an approved local integration with future deployment policy
  unresolved; a deployment interview is unnecessary to this operation.
- **Legacy profile:** a previously complete release profile lacks the optional
  context-tool link; adding that documentation must not revoke readiness.

Six Boolean implementation checks and four policy checks form a 0–1 score. Full completion requires
all checks and a successful agent process with reported usage. Graders run
outside the agent workspace. Implementation also requires changed tests and an
observed successful test command. Policy grading requires the exact requested
gate in an observed successful command plus an independent gate rerun; this
does not depend on intermediate stdout surviving shell-output filtering.
Policy fixtures contain synthetic approved values;
these trials evaluate policy-check completion, not production rollout quality.
Use the fixture logs to inspect whether the conclusion follows the observed
command. Scores are operational outcomes under the intended corrected contract,
not a claim that a baseline agent disobeyed its older instructions.

Metrics:

- **Clarification turns:** trials whose final structured response requests an
  answer, with question count recorded separately. Trials have one user turn;
  this does not measure full interviews or rounds after a user response.
- **Tool calls:** distinct command/MCP/search/edit event IDs, counting starts
  and completions once. A shell command may contain several subprocesses.
- **Tokens:** actual `turn.completed.usage`, including total input, cached input,
  output, and reasoning output when provided. Cached input is a subset of input;
  reasoning output is a subset of output. Missing usage is unknown, never zero.
- **Completion:** external behavioral assertions, check execution, scope, and
  accurate status. Inspect failed or interrupted trials; never discard them
  silently from summaries.

Compare per-scenario paired trials as well as aggregate results. Two repetitions
are a small pilot, not statistical proof. Caching/order, the common host prompt,
and agent variance affect totals. Do not describe shorter skill text or cheaper
early failure as an efficiency gain without maintained completion quality.

After a grader correction, rescore retained workspaces without more model calls:

```bash
python3 scripts/summarize_agent_benchmark.py \
  --baseline-run evals/results/agents-BASELINE \
  --candidate-run evals/results/agents-CANDIDATE
```

This preserves original results, adds `rescored-results.json` to each selected
run, and writes `comparison.json` in the candidate run. Use `--arm candidate`
with the runner for an explicitly documented corrected-candidate rerun rather
than paying to repeat unchanged controls. Retain failed intermediate candidates;
do not pool versions or silently exclude failures.

Codex JSON events and usage follow the documented
[non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).
