# Architecture changes: real-agent regression pilot

Date: 2026-09-07. Baseline: `a00d263ee4d7532d1d41f458f2f7d1b95469779a`.
Candidate: plugin 0.2.0, measured in the `fix/architecture-and-agent-evals`
worktree and published with this report on the `eval` branch. Content hashes
below identify the tested snapshot independently of its later commit.

## Outcome

The final candidate completed all six trials; baseline completed two. Input
tokens fell 22.6%, output tokens 22.8%, and tool calls 11.9% in this pilot.
These are observed results, not a statistically established general saving.

| Metric, six trials per arm | Baseline | Final candidate |
| --- | ---: | ---: |
| Full completion | 2/6 | 6/6 |
| Mean Boolean-check quality | 70.8% | 100% |
| Clarification turns / questions | 1 / 2 | 0 / 0 |
| Tool calls | 42 | 37 |
| Input tokens | 931,861 | 720,883 |
| Cached input tokens (subset) | 784,128 | 597,376 |
| Uncached input tokens | 147,733 | 123,507 |
| Output tokens | 13,589 | 10,485 |
| Reasoning output tokens (subset) | 5,583 | 3,540 |

The cleanest efficiency comparison is implementation: both versions passed
2/2, while input tokens fell 29.6% (455,670 → 320,947), tool calls fell
34.8% (23 → 15), and output tokens fell 23.0% (6,146 → 4,731).
Integration used **more** calls (12 → 15) while reaching a correct conclusion
instead of stopping early. Legacy-profile calls were unchanged (7 → 7).
Do not describe all individual scenarios as needing fewer tools.

## What changed

- One bundled parser/schema now serves the standalone workflow and plugin hook.
  Explicit versioned field sets replace deriving requirements from Markdown.
  Legacy profiles remain valid without an optional context-tool link.
- Blank fields cannot consume headings; duplicate labels fail consistently;
  fenced examples are ignored; unknown schema versions are rejected.
- `UNRESOLVED` is a leading status marker, not a forbidden word inside approved
  prose. The real runs exposed this additional false-positive bug.
- Build, integration, and deployment/release are distinct boundaries, with
  18, 46, and 53 required fields. Merge-only work no longer needs deployment policy.
- Preflight follows the approved remote/base, rejects conflicting overrides,
  and retains worktree and protected-branch safeguards.
- Onboarding reminders require repository opt-in, support explicit dismissal,
  and default to Build rather than demanding the full release profile.
- Workflow/onboarding entrypoints use progressive disclosure, reuse valid facts
  and checks, and preserve authority limits. Workflow plus Build text shrank
  from 2,545 to 1,444 whitespace-delimited words (43.3%). This size reduction is
  separate from the actual runtime token measurements above.

## Trial-level evidence

All rows use the same final grader. C = clarification turns, not question count.

| Arm | Scenario | Repeat | Passed | Tools | C | Input | Cached input | Output |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | Implementation | 1 | yes | 15 | 0 | 249,245 | 207,360 | 3,430 |
| Baseline | Implementation | 2 | yes | 8 | 0 | 206,425 | 179,712 | 2,716 |
| Baseline | Integration | 1 | no | 5 | 0 | 129,876 | 112,000 | 2,505 |
| Baseline | Integration | 2 | no | 7 | 1 | 173,943 | 138,496 | 2,984 |
| Baseline | Legacy profile | 1 | no | 3 | 0 | 74,425 | 62,592 | 879 |
| Baseline | Legacy profile | 2 | no | 4 | 0 | 97,947 | 83,968 | 1,075 |
| Candidate | Implementation | 1 | yes | 7 | 0 | 127,452 | 105,216 | 2,322 |
| Candidate | Implementation | 2 | yes | 8 | 0 | 193,495 | 163,328 | 2,409 |
| Candidate | Integration | 1 | yes | 6 | 0 | 95,356 | 82,816 | 1,919 |
| Candidate | Integration | 2 | yes | 9 | 0 | 135,573 | 108,544 | 1,977 |
| Candidate | Legacy profile | 1 | yes | 3 | 0 | 73,615 | 62,208 | 773 |
| Candidate | Legacy profile | 2 | yes | 4 | 0 | 95,392 | 75,264 | 1,085 |

Baseline integration repeat 2 asked Morgan for a deployment pipeline and a
Context pipeline value despite the merge-only request. The candidate required
neither. Baseline agents correctly respected their older failed gates; this
comparison measures workflow outcomes, not agent disobedience.

## Method and reproducibility

Real signed-in Codex CLI runs: `codex-cli 0.149.0`, `gpt-5.6-sol`, medium
reasoning, two concurrent jobs. Each trial has a fresh local Git repository,
task-owned linked worktree, identical synthetic approved legacy policy, and
one user turn. No remote Git mutation, production access, or actual release.
Plugins, hooks, apps, and delegation are disabled; agents explicitly read
fixture instructions and the installed skills. Hook behavior is unit-tested,
not measured by these agent trials.

Six implementation checks cover public-function behavior (including whitespace,
punctuation and ASCII-only lowercasing), passing regression tests, added/changed
tests, observed test execution, scoped changes/no commit, and truthful completion.
Four policy checks cover correct conclusion backed by a passing gate, observed
invocation of the exact requested gate, unchanged fixture, and no needless
clarification. Mean quality averages each trial's fraction of passing checks;
full completion requires every check and successful process/usage capture.

Tools count unique command/search/MCP/edit event IDs, not subprocesses inside
a shell command. Tokens are actual `turn.completed.usage`; cached input and
reasoning output must not be added a second time. Clarification records a
request for an answer in the final structured response. No multi-turn interview
was completed, so the observed 1 → 0 is only one avoided clarification event.

Run commands and metric definitions: [eval protocol](../../evals/README.md).
The final comparison uses baseline rows from `agents-e6etn8ip` and candidate
rows from `agents-lwbpwnnx`. Artifacts remain locally under `evals/results/`:
prompts, full events, final responses, fixtures, original and rescored results,
metadata, and final `agents-lwbpwnnx/comparison.json`.

Content SHA-256 identifiers (skills and hooks, paths plus bytes):

- Baseline: `b539ff6bad054f579bde71e68f90aad56cf383879836acc212a638f8910649c1`
- Intermediate candidate: `ce53e2792dddfb5796a6e93fe2b47af0ac713e28cbcdea211cdf1d4e7415791d`
- Final candidate: `15d9d3d0bd1d50aadbac4331588269777b037a4b9167308a7013be8865393df7`
- Final runner/grader: `f41da0e817d0785a39c516b4c02f6695e5eecc27e5f81a9c48c9164e9cca751a`

The final source skills/hooks hash was verified against the tested snapshot.

## Calibration, failures, and measurement corrections

1. Initial calibration `agents-g_ljv0hd` filled the profile with generic approval
   placeholders and accidentally rewrote explanatory text. Five completed
   records were retained, the batch was stopped, and this invalid fixture was
   excluded from efficacy comparisons. Interrupted runs have unknown usage.
2. The corrected-fixture batch `agents-e6etn8ip` ran all 12 trials. Its intermediate
   candidate passed implementation 2/2 but failed all four policy trials because
   approved prose mentioning “unresolved P1/P2 review findings” was misclassified.
   These are real product failures, not discarded calibration. They remain in
   the audit and are not pooled with the final fixed candidate.
3. After fixing that parser defect and adding a regression test, only the six
   candidate trials were repeated. Unchanged baseline controls were reused to
   avoid six unnecessary model runs. This makes final-arm order nonrandom and
   potentially affected by time/cache differences.
4. Independent review strengthened the grader to require the correct gate,
   changed tests, observed tests, and bounded probes. Successful intermediate
   stdout was missing from some chained shell outputs, so policy grading now
   also independently reruns the gate. Both batches were rescored without new
   inference; original results were preserved. A relative-path bug in the
   rescore utility was corrected before producing this report.

Across all 23 completed benchmark records, including calibration and intermediate
failures, reported usage was 3,291,127 input tokens (2,730,752 cached) and 46,127
output tokens. This excludes unknown interrupted usage, the CLI smoke check,
and this implementation/review conversation; it is not a total account bill.

## Verification and limits

- 55 unit tests passed; catalog validation passed for 13 skills / 13 eval files,
  with 42/42 positive rank-1 routing cases; all four changed skill entrypoints
  passed the skill validator; `git diff --check` passed.
- Unit coverage includes blank/duplicate fields, schema compatibility,
  gate separation, hook opt-in/dismissal, alternate bases and conflicting overrides.
- The skill-creator guidance shaped progressive disclosure and independent
  verification. No global skill installation or active plugin update was made.
- This is a small, targeted regression pilot, not a representative workload
  benchmark. Two repeats, shared host context, cache state, run order, and model
  variance limit causal attribution. There is no ablation separating each change.
- Production rollout quality, complex UI evidence workflows, full onboarding
  interviews, and automatic plugin activation remain unmeasured. Existing UI
  evidence requirements were retained rather than trimmed without supporting tests.
- Implementation and this report were published on `eval` by user request;
  main was unchanged at the baseline when the benchmark ran. Raw local transcripts and
  disposable fixtures are intentionally not committed.
