# Model routing

Choose a role tier from task evidence, then map that tier to an actual model available in the current harness. Keep the model-to-tier mapping in project or harness configuration; do not hardcode vendor model names into the orchestration contract.

Assess each task on complexity, uncertainty, blast radius, verification importance, and cost. Start with the least expensive tier reasonably expected to complete the task correctly.

## Tier A — frontier reasoning

Use for high-ambiguity architecture, difficult root-cause analysis, security- or privacy-sensitive changes, complex migrations, cross-system decisions, high-blast-radius work, and critical independent review.

## Tier B — strong engineering

Use for feature implementation, non-trivial fixes, API or database integration, significant refactoring, complex tests, performance work, and bounded architectural reasoning.

## Tier C — efficient execution

Use for repository reconnaissance, structured extraction, boilerplate, mechanical refactoring, straightforward UI work, focused unit tests, documentation, and type or lint corrections whose behavior is already specified.

## Escalation

Escalate or reframe when evidence shows that:

- the same underlying problem has failed twice;
- the root cause remains unclear;
- requirements become materially ambiguous;
- blast radius or cross-system coupling increases; or
- security, privacy, migration, or data-integrity risk appears.

Do not claim a particular model was selected when the harness exposes only a generic worker. Record the available worker role and the intended tier instead. Do not spend Tier A capacity reviewing trivial mechanical work unless its context creates material risk.
