#!/usr/bin/env python3
"""Audit source integrity, lecture spans, and substantive independent page ledgers."""
import hashlib
import json
import re
import sys
from pathlib import Path

import jt_reader

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {"course-early": (1, 480), "course-middle": (481, 960),
          "course-late": (961, 1458), "jibengong": (1, 128)}
REVIEW_NAMES = {"course-early": "early", "course-middle": "middle", "course-late": "late",
                "jibengong": "jibengong"}


def valid_reference(reference, map_text, supplement_text, scope):
    """Resolve card IDs, qualified section references, and source-page table references."""
    key = reference.split(":")[-1]
    if re.fullmatch(r"§\d+@\d+", key):
        section, page = map(int, key[1:].split("@"))
        return (scope[0] <= page <= scope[1]
                and re.search(rf"(?m)^## {section}\. ", map_text) is not None)
    if reference.startswith("maps/jibengong.md:"):
        if key == "来源说明":
            return bool(map_text)
        match = re.fullmatch(r"(?:例子|限定)p(\d+)(?:[–-](\d+))?", key)
        return bool(match and 1 <= int(match[1]) <= int(match[2] or match[1]) <= 128)
    return re.search(r"(?<![\w-])" + re.escape(key) + r"(?![\w-])",
                     map_text + "\n" + supplement_text) is not None


def main():
    failures = []
    report = {"corpus": jt_reader.verify(), "initial_declared_reading_coverage": {},
              "independent_second_review": {}}
    for name, (first, last) in SCOPES.items():
        path = ROOT / "references/maps" / f"{name}-coverage.json"
        if not path.exists():
            failures.append(f"Missing coverage record: {name}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        actual = []
        for batch in data["batches"]:
            if batch.get("read") is True:
                actual.extend(range(batch["start"], batch["end"] + 1))
        expected = list(range(first, last + 1))
        report["initial_declared_reading_coverage"][name] = {
            "declared_read_pages": len(actual), "expected_pages": len(expected), "complete": actual == expected}
        if actual != expected:
            failures.append(f"Incomplete/duplicate/out-of-order reading coverage: {name}")
        map_path = ROOT / "references/maps" / f"{name}.md"
        if not map_path.exists() or len(map_path.read_text(encoding="utf-8")) < 1000:
            failures.append(f"Missing or empty substantive map: {name}")
            continue
        review_name = REVIEW_NAMES[name]
        ledger_path = ROOT / "references/review" / f"{review_name}-page-ledger.json"
        supplement_path = ROOT / "references/review" / f"{review_name}-supplement.md"
        if not ledger_path.exists() or not supplement_path.exists():
            failures.append(f"Missing independent second review: {name}")
            continue
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        rows = ledger.get("pages", [])
        actual_pages = [row.get("page") for row in rows]
        complete = actual_pages == expected
        if not complete:
            failures.append(f"Independent review incomplete/duplicate/out of order: {name}")
        invalid_pages, unresolved = [], []
        map_text = map_path.read_text(encoding="utf-8")
        supplement_text = supplement_path.read_text(encoding="utf-8")
        for row in rows:
            substantive = (isinstance(row.get("topics"), list) and bool(row["topics"])
                           and all(isinstance(t, str) and t.strip() for t in row["topics"])
                           and isinstance(row.get("examples"), list)
                           and isinstance(row.get("covered_by"), list)
                           and (bool(row["covered_by"]) or (name != "jibengong"
                                and (row["page"] < 6 or row["page"] > 1454)))
                           and isinstance(row.get("notes"), str) and bool(row["notes"].strip()))
            if not substantive or (name == "jibengong" and row.get("visual_checked") is not True):
                invalid_pages.append(row.get("page"))
            for reference in row.get("covered_by", []):
                if not valid_reference(reference, map_text, supplement_text, (first, last)):
                    unresolved.append({"page": row.get("page"), "reference": reference})
        if invalid_pages:
            failures.append(f"Non-substantive/unverified page ledger: {name}: {invalid_pages}")
        if unresolved:
            failures.append(f"Unresolved review references: {name}: {unresolved}")
        report["independent_second_review"][name] = {
            "pages": len(rows), "expected_pages": len(expected), "complete": complete,
            "first": actual_pages[0] if rows else None, "last": actual_pages[-1] if rows else None,
            "invalid_page_records": invalid_pages, "unresolved_references": unresolved,
            "ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
            "supplement_characters": len(supplement_text),
            "visual_checked_pages": sum(row.get("visual_checked") is True for row in rows)}
    body = {p["page"]: p["text"] for p in jt_reader.load_pages("neiqipian")}
    first_lesson = jt_reader.lesson_range(1)
    expected_body = body[6][first_lesson["start_offset"]:] + "".join(body[p] for p in range(7, 1455))
    actual_body = "".join(p["text"] for n in range(1, 95) for p in jt_reader.lesson_pages(n))
    report["lecture_spans"] = {"lectures": 94, "body_covered_once": actual_body == expected_body}
    if actual_body != expected_body:
        failures.append("Lecture spans omit or duplicate shared boundary text")
    corrections = json.loads((ROOT / "references/corpus/ocr-corrections.json").read_text(encoding="utf-8"))
    report["ocr_annotations"] = len(corrections["corrections"])
    if any(not (1 <= c["page"] <= 128) or not c.get("verified") or not c.get("note")
           for c in corrections["corrections"]):
        failures.append("Invalid OCR annotation")
    links_checked = 0
    for path in [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "references").rglob("*.md"))]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"\w+://", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0].strip("<>")
            if target and not (path.parent / target).resolve().exists():
                failures.append(f"Broken link: {path.relative_to(ROOT)} -> {target}")
            links_checked += 1
    report["internal_links_checked"] = links_checked
    report["failures"] = failures
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
