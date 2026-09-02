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
