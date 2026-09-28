#!/usr/bin/env python3
"""Validate Monomind skill structure, eval coverage, and lexical routing."""

from __future__ import annotations

import json
import math
import re
import string
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote as url_unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CASES_DIR = ROOT / "evals" / "cases"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORD_RE = re.compile(r"[a-z0-9]+")
FIELD_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
INLINE_LINK_START_RE = re.compile(r"!?\[[^\]\n]+\]\(")
REFERENCE_USE_RE = re.compile(r"!?\[([^\]\n]+)\]\[([^\]\n]*)\]")
REFERENCE_DEF_RE = re.compile(r"^ {0,3}\[([^\]\n]+)\]:\s*(<[^>\n]+>|\S+)")
MARKDOWN_PUNCTUATION_ESCAPE_RE = re.compile(r"\\([" + re.escape(string.punctuation) + r"])")

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


def read_scalar(value: str, location: str, validation: Validation) -> str | None:
    """Read the single-line scalar subset used by this catalog, without a YAML dependency."""
    if value.startswith('"'):
        try:
            parsed, end = json.JSONDecoder().raw_decode(value)
        except json.JSONDecodeError:
            validation.error(f"{location}: invalid double-quoted YAML scalar")
            return None
        if not isinstance(parsed, str) or not valid_comment_suffix(value[end:]):
            validation.error(f"{location}: invalid double-quoted YAML scalar")
            return None
        return parsed
    if value.startswith("'"):
        match = re.match(r"'((?:[^']|'')*)'", value)
        if not match or not valid_comment_suffix(value[match.end():]):
            validation.error(f"{location}: invalid single-quoted YAML scalar")
            return None
        return match.group(1).replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not value or value.startswith("#"):
        validation.error(f"{location}: comment-only or empty YAML scalar")
        return None
    if re.search(r":(?:\s|$)", value) or value.startswith(("[", "{", "|", ">")):
        validation.error(f"{location}: quote or simplify the unsupported YAML scalar")
        return None
    return value


def valid_comment_suffix(suffix: str) -> bool:
    return not suffix or bool(re.fullmatch(r"\s+#.*", suffix))


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
    mapping: str | None = None
    seen: set[tuple[str | None, str]] = set()
    for number, line in enumerate(text[4:marker].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        location = f"{path.relative_to(ROOT)}:{number}"
        indentation = len(line) - len(line.lstrip(" "))
        if "\t" in line[:len(line) - len(line.lstrip())] or indentation not in {0, 2}:
            validation.error(f"{location}: unsupported or tabbed YAML indentation")
            continue
        if indentation == 2 and mapping is None:
            validation.error(f"{location}: nested field without a mapping")
            continue
        key, separator, value = line.strip().partition(":")
        if not separator or not FIELD_RE.fullmatch(key) or (value and not value[0].isspace()):
            validation.error(f"{location}: malformed YAML field")
            continue
        identity = (mapping if indentation == 2 else None, key)
        if identity in seen:
            validation.error(f"{location}: duplicate YAML field {key!r}")
            continue
        seen.add(identity)
        value = value.strip()
        if not value:
            if indentation == 2:
                validation.error(f"{location}: nested mappings are unsupported")
            else:
                mapping = key
            continue
        if indentation == 0:
            mapping = None
        scalar = read_scalar(value, location, validation)
        if scalar is not None and indentation == 0:
            result[key] = scalar

    if "TODO" in text or "[TODO" in text:
        validation.error(f"{path.relative_to(ROOT)}: unfinished scaffold placeholder")
    return result


def without_inline_code(line: str) -> str:
    """Blank complete backtick code spans while preserving line positions."""
    result = list(line)
    index = 0
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue
        end = index
        while end < len(line) and line[end] == "`":
            end += 1
        marker = line[index:end]
        closing = line.find(marker, end)
        if closing < 0:
            index = end
            continue
        result[index:closing + len(marker)] = " " * (closing + len(marker) - index)
        index = closing + len(marker)
    return "".join(result)


def inline_destinations(line: str):
    """Yield single-line inline link destinations, respecting balanced parentheses."""
    for match in INLINE_LINK_START_RE.finditer(line):
        start = match.end()
        if start >= len(line):
            continue
        if line[start] == "<":
            end = line.find(">", start + 1)
            if end >= 0:
                yield line[start + 1:end]
            continue
        depth = 0
        index = start
        while index < len(line):
            char = line[index]
            if char == "\\" and index + 1 < len(line):
                index += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            index += 1
        if index < len(line) and line[start:index]:
            yield line[start:index]


def reference_key(label: str) -> str:
    return " ".join(label.split()).casefold()


def validate_local_links(skill_dir: Path, validation: Validation) -> None:
    """Check single-line inline and explicit reference links in skill Markdown.

    Fenced and inline code are ignored. Shortcut references, HTML links, and
    multiline destinations are outside this deliberately bounded check.
    """
    root = skill_dir.resolve()
    for document in sorted(skill_dir.rglob("*.md")):
        fence_marker: str | None = None
        fence_length = 0
        definitions: set[str] = set()
        references: list[tuple[str, str]] = []
        destinations: list[tuple[str, str]] = []
        for number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), start=1):
            fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if fence:
                marker, rest = fence.groups()
                if fence_marker is None:
                    fence_marker, fence_length = marker[0], len(marker)
                elif marker[0] == fence_marker and len(marker) >= fence_length and not rest.strip():
                    fence_marker = None
                continue
            if fence_marker is not None:
                continue
            line = without_inline_code(line)
            location = f"{document.relative_to(ROOT)}:{number}"
            definition = REFERENCE_DEF_RE.match(line)
            if definition:
                definitions.add(reference_key(definition.group(1)))
                destinations.append((definition.group(2).strip("<>"), location))
                continue
            destinations.extend((target, location) for target in inline_destinations(line))
            for use in REFERENCE_USE_RE.finditer(line):
                references.append((reference_key(use.group(2) or use.group(1)), location))

        for key, location in references:
            if key not in definitions:
                validation.error(f"{location}: undefined reference: {key}")
        for target, location in destinations:
            normalized_target = MARKDOWN_PUNCTUATION_ESCAPE_RE.sub(r"\1", target)
            parsed = urlsplit(normalized_target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local = (document.parent / url_unquote(parsed.path)).resolve()
            if not local.is_relative_to(root):
                validation.error(f"{location}: local link escapes the standalone skill: {target}")
            elif not local.is_file():
                validation.error(f"{location}: broken local link: {target}")


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
        validate_local_links(folder, validation)
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
