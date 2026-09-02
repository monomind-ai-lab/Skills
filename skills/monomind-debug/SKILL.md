---
name: monomind-debug
description: "Diagnose failing, incorrect, intermittent, or slow behavior with a tight reproducible feedback loop. Use when tests, builds, runtime flows, or performance regress unexpectedly. Diagnosis requests produce a cause report; apply a fix only when the user also authorizes one."
---

# Monomind Debug

Make the failure observable, reduce it, falsify hypotheses, and identify the cause before changing production behavior.

## Establish the mode and evidence

1. Determine whether the request is diagnosis-only or includes implementation of a fix. Do not infer mutation authority from the word "diagnose."
2. Preserve the original error, timestamps, revision, environment, inputs, and reproduction steps. Redact credentials, personal data, and customer content.
3. Stop unrelated feature work while the observed failure remains unexplained.

## Tighten the red loop

1. Build the fastest trustworthy feedback loop that goes **red** on this failure: a focused test, deterministic script, recorded request, browser flow, benchmark, or production-like probe.
2. Confirm that the loop detects the failure for the right reason. A failing command with an unrelated setup error is not a reproduction.
3. Minimize the case while keeping it red. Remove inputs, dependencies, concurrency, and layers one at a time.
4. For intermittent failures, run repeated trials and record frequency, timing, seed, and environment instead of treating one pass as disproof.

## Find the cause

1. Localize the first boundary where expected and actual behavior diverge.
2. Write a small set of falsifiable hypotheses ranked by evidence and test cost.
3. Change one variable or add one observation at a time. Instrument boundaries and state transitions; avoid broad speculative edits.
4. State the causal chain from trigger through the faulty invariant to the visible symptom. Distinguish verified cause, supporting evidence, and remaining uncertainty.

## Fix only when authorized

1. Preserve the red reproduction as a regression check.
2. Apply the smallest change at the causal boundary.
3. Show the focused loop turning green, then run the relevant regression gates and runtime proof.
4. Remove temporary instrumentation and confirm it did not hide the failure.

If no trustworthy reproduction is possible, do not claim a root cause. Report the strongest bounded hypothesis, evidence gaps, added observations, and the next event that would confirm or falsify it.

## Completion criteria

- The feedback loop is documented and fails for the observed defect, not an incidental error.
- The cause report separates symptom, trigger, broken invariant, and causal boundary.
- Alternative hypotheses were falsified or explicitly left open.
- Any authorized fix is guarded by a regression check and relevant end-to-end evidence.
- Sensitive evidence is redacted and temporary diagnostics are removed or intentionally retained.
