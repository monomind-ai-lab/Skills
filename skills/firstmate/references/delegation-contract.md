# Delegation contract

Give each agent a bounded assignment containing the fields below. Omit a field only when it genuinely does not apply; do not replace missing project facts with guesses.

## Objective

State the observable outcome, not a list of motions.

## Scope and ownership

Name the relevant modules, systems, allowed paths or artifacts, and explicit exclusions. Identify the task owner and any shared resource that requires coordination.

## Context pointers

Point to the authoritative specification, decision, issue, interfaces, and prior evidence. Avoid repository-wide context dumps and copied source when a stable pointer exists.

## Constraints

State architecture, compatibility, security, privacy, migration, repository-policy, and behavior constraints that must remain true.

## Dependencies

Name prerequisite tasks, supplied interfaces, expected consumers, and what may run in parallel. Define the condition that unblocks dependent work.

## Acceptance criteria

List observable requirements, boundary and failure behavior, and the completion condition.

## Verification

Name repository-native focused and regression checks, runtime or visual proof, and any independent review required. The worker must report commands and actual results; green output is evidence, not permission to integrate.

## Git and delivery

Follow the repository's branch/worktree policy. Name the expected deliverable: implementation branch, change request, investigation report, design, test evidence, or another concrete artifact. Do not grant commit, push, pull-request, merge, or deployment authority unless already supplied.

## Return contract

Require a concise result containing changed artifacts, acceptance status, verification, residual risks, blockers, and the exact revision or branch. Instruct the worker not to revert or absorb unrelated work.
