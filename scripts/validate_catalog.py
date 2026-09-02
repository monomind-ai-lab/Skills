#!/usr/bin/env python3
"""Validate Monomind skill structure, eval coverage, and lexical routing."""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CASES_DIR = ROOT / "evals" / "cases"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORD_RE = re.compile(r"[a-z0-9]+")

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "both", "by",
    "do", "does", "for", "from", "has", "in", "into", "is", "it", "its",
    "merely", "of", "on", "or", "the", "their", "this", "to", "use", "when",
    "where", "with", "without", "work", "user", "asks", "needs", "need",
}

ALIASES = {
    "acceptance": "accept",
    "accepted": "accept",
    "criteria": "criterion",
    "deploy": "release",
    "deployment": "release",
    "deploying": "release",
    "diagnose": "debug",
    "diagnosing": "debug",
    "diagnosis": "debug",
    "handover": "handoff",
    "implementation": "implement",
    "implementing": "implement",
    "launch": "release",
    "launching": "release",
    "modules": "module",
    "planning": "plan",
    "proof": "evidence",
    "pull": "pr",
    "requests": "request",
    "reviewing": "review",
    "specification": "spec",
    "specifications": "spec",
    "tasks": "task",
    "testing": "test",
}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def read_frontmatter(path: Path, validation: Validation) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        validation.error(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    marker = text.find("\n---\n", 4)
    if marker < 0:
        validation.error(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
        return {}

    result: dict[str, str] = {}
    for line in text[4:marker].splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = unquote(value)

    if "TODO" in text or "[TODO" in text:
        validation.error(f"{path.relative_to(ROOT)}: unfinished scaffold placeholder")
    return result


def read_ui_metadata(path: Path, skill_name: str, validation: Validation) -> None:
    relative = path.relative_to(ROOT)
    if not path.exists():
        validation.error(f"{relative}: missing UI metadata")
        return
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s*{key}:\s*\"([^\"]*)\"\s*$", text, re.MULTILINE)
        if not match:
            validation.error(f"{relative}: missing quoted interface.{key}")
            continue
        fields[key] = match.group(1)

    short = fields.get("short_description", "")
    if short and not 25 <= len(short) <= 64:
        validation.error(f"{relative}: short_description must be 25-64 characters")
    prompt = fields.get("default_prompt", "")
    if prompt and f"${skill_name}" not in prompt:
        validation.error(f"{relative}: default_prompt must mention ${skill_name}")


def normalize_word(word: str) -> str:
    word = ALIASES.get(word, word)
    if word in ALIASES:
        return ALIASES[word]
    if len(word) > 5 and word.endswith("ing"):
        word = word[:-3]
    elif len(word) > 4 and word.endswith("ed"):
        word = word[:-2]
    elif len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return ALIASES.get(word, word)


def tokenize(text: str) -> list[str]:
    words = []
    for raw in WORD_RE.findall(text.lower().replace("-", " ")):
        if raw not in STOP_WORDS:
            word = normalize_word(raw)
            if word and word not in STOP_WORDS:
                words.append(word)
    return words


def make_vectors(documents: dict[str, str]):
    tokens = {name: tokenize(text) for name, text in documents.items()}
    document_frequency: Counter[str] = Counter()
    for words in tokens.values():
        document_frequency.update(set(words))
    count = len(tokens)
    idf = {
        word: math.log((count + 1) / (frequency + 1)) + 1
        for word, frequency in document_frequency.items()
    }

    def vectorize(text_or_words):
        words = text_or_words if isinstance(text_or_words, list) else tokenize(text_or_words)
        frequencies = Counter(words)
        default_idf = math.log(count + 1) + 1
        return {
            word: frequency * idf.get(word, default_idf)
            for word, frequency in frequencies.items()
        }

    return {name: vectorize(words) for name, words in tokens.items()}, vectorize


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    numerator = sum(value * right.get(word, 0.0) for word, value in left.items())
    if not numerator:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def load_catalog(validation: Validation):
    skills: dict[str, dict[str, str]] = {}
    for folder in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        skill_path = folder / "SKILL.md"
        if not skill_path.exists():
            validation.error(f"{folder.relative_to(ROOT)}: missing SKILL.md")
            continue
        frontmatter = read_frontmatter(skill_path, validation)
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if not NAME_RE.fullmatch(name):
            validation.error(f"{skill_path.relative_to(ROOT)}: invalid skill name {name!r}")
        if name != folder.name:
            validation.error(f"{skill_path.relative_to(ROOT)}: name must match folder")
        if not description or len(description) < 40:
            validation.error(f"{skill_path.relative_to(ROOT)}: description is missing or too vague")
        if len(description) > 500:
            validation.error(f"{skill_path.relative_to(ROOT)}: description exceeds 500 characters")
        read_ui_metadata(folder / "agents" / "openai.yaml", name, validation)
        if name:
            skills[name] = {"description": description}
    return skills


def load_cases(skills: dict[str, dict[str, str]], validation: Validation):
    cases: dict[str, dict] = {}
    for path in sorted(CASES_DIR.glob("*.json")):
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            validation.error(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
            continue
        name = case.get("skill_name")
        if name not in skills:
            validation.error(f"{path.relative_to(ROOT)}: unknown skill_name {name!r}")
            continue
        if path.stem != name:
            validation.error(f"{path.relative_to(ROOT)}: filename must match skill_name")
        trigger = case.get("trigger", {})
        positives = trigger.get("positive", [])
        negatives = trigger.get("negative", [])
        evals = case.get("evals", [])
        if len(positives) < 3:
            validation.error(f"{path.relative_to(ROOT)}: needs at least 3 positive triggers")
        if len(negatives) < 2:
            validation.error(f"{path.relative_to(ROOT)}: needs at least 2 negative triggers")
        if not evals:
            validation.error(f"{path.relative_to(ROOT)}: needs at least 1 behavioral eval")
        for item in positives:
            if not item.get("prompt") or not isinstance(item.get("top_k", 1), int):
                validation.error(f"{path.relative_to(ROOT)}: malformed positive trigger")
        for item in negatives:
            owner = item.get("owner")
            if not item.get("prompt") or owner not in skills or owner == name:
                validation.error(f"{path.relative_to(ROOT)}: negative trigger needs another valid owner")
        for item in evals:
            if item.get("kind") not in {"dialogue", "execution"}:
                validation.error(f"{path.relative_to(ROOT)}: eval kind must be dialogue or execution")
            if not item.get("prompt") or not item.get("expected_output"):
                validation.error(f"{path.relative_to(ROOT)}: eval needs prompt and expected_output")
            if len(item.get("expectations", [])) < 3:
                validation.error(f"{path.relative_to(ROOT)}: eval needs at least 3 expectations")
        cases[name] = case

    missing = sorted(set(skills) - set(cases))
    extra = sorted(set(cases) - set(skills))
    if missing:
        validation.error(f"missing eval cases: {', '.join(missing)}")
    if extra:
        validation.error(f"orphan eval cases: {', '.join(extra)}")
    return cases


def validate_routing(skills, cases, validation: Validation) -> tuple[int, int]:
    descriptions = {name: item["description"] for name, item in skills.items()}
    vectors, vectorize = make_vectors(descriptions)
    positive_count = 0
    rank_one_count = 0

    def ranking(prompt: str):
        prompt_vector = vectorize(prompt)
        return sorted(
            ((name, cosine(prompt_vector, vector)) for name, vector in vectors.items()),
            key=lambda item: (-item[1], item[0]),
        )

    for name, case in sorted(cases.items()):
        for item in case["trigger"]["positive"]:
            ranked = ranking(item["prompt"])
            names = [candidate for candidate, _ in ranked]
            rank = names.index(name) + 1
            top_k = item.get("top_k", 1)
            positive_count += 1
            rank_one_count += rank == 1
            if rank > top_k:
                top = ", ".join(f"{candidate}={score:.3f}" for candidate, score in ranked[:3])
                validation.error(
                    f"routing: {name} ranked {rank} (wanted top {top_k}) for {item['prompt']!r}; {top}"
                )
            elif rank > 1:
                validation.warn(
                    f"routing tolerance: {name} ranked {rank} within top {top_k} "
                    f"for {item['prompt']!r}"
                )

        for item in case["trigger"]["negative"]:
            ranked = dict(ranking(item["prompt"]))
            owner = item["owner"]
            if ranked[owner] <= ranked[name]:
                validation.error(
                    f"routing: negative owner {owner} ({ranked[owner]:.3f}) did not outrank "
                    f"{name} ({ranked[name]:.3f}) for {item['prompt']!r}"
                )

    names = sorted(vectors)
    for index, left_name in enumerate(names):
        for right_name in names[index + 1 :]:
            similarity = cosine(vectors[left_name], vectors[right_name])
            if similarity >= 0.72:
                validation.error(
                    f"description collision: {left_name} vs {right_name} = {similarity:.3f}"
                )
            elif similarity >= 0.52:
                validation.warn(
                    f"description similarity: {left_name} vs {right_name} = {similarity:.3f}"
                )
    return rank_one_count, positive_count


def main() -> int:
    validation = Validation()
    if not SKILLS_DIR.exists() or not CASES_DIR.exists():
        print("catalog directories are missing", file=sys.stderr)
        return 1

    skills = load_catalog(validation)
    cases = load_cases(skills, validation)
    rank_one, positive_count = validate_routing(skills, cases, validation) if cases else (0, 0)

    for warning in validation.warnings:
        print(f"WARN: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}")

    rate = (100 * rank_one / positive_count) if positive_count else 0.0
    print(
        f"Checked {len(skills)} skills and {len(cases)} eval files; "
        f"positive trigger rank-1 rate {rank_one}/{positive_count} ({rate:.1f}%)."
    )
    if validation.errors:
        print(f"Validation failed with {len(validation.errors)} error(s).")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
