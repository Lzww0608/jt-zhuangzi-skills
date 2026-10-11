#!/usr/bin/env python3
"""Locate all 94 lecture headings and preserve text across shared PDF pages."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "references/corpus"


def main():
    path = CORPUS / "lessons.json"
    lessons = json.loads(path.read_text(encoding="utf-8"))
    pages = [json.loads(line) for line in (CORPUS / "neiqipian/pages.jsonl").read_text(encoding="utf-8").splitlines()]
    for lesson in lessons:
        page = pages[lesson["start"] - 1]["text"]
        pattern = r"(?m)^[ \t]*" + str(lesson["number"]).zfill(2) + r"[ \t]+[^\n]+"
        matches = list(re.finditer(pattern, page))
        if len(matches) != 1:
            raise ValueError(f"Expected one source heading: lesson {lesson['number']}, page {lesson['start']}")
        lesson["start_offset"] = matches[0].start()
        lesson["source_heading"] = matches[0].group().strip()
    report = []
    for index, lesson in enumerate(lessons):
        following = lessons[index + 1] if index + 1 < len(lessons) else None
        lesson["end"] = following["start"] if following else 1454
        lesson["end_offset"] = following["start_offset"] if following else len(pages[1453]["text"])
        report.append({"number": lesson["number"], "start_page": lesson["start"],
                       "start_offset": lesson["start_offset"], "end_page": lesson["end"],
                       "end_offset": lesson["end_offset"], "source_heading": lesson["source_heading"],
                       "characters_before_heading_on_start_page": lesson["start_offset"],
                       "before_heading_note": "includes any page header and previous lecture tail; not a semantic tail count"})
    path.write_text(json.dumps(lessons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dest = ROOT / "references/review/lesson-boundaries.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"method": "94 source headings found uniquely on catalog start pages; half-open character spans split shared pages without discarding previous tails", "offset_unit": "Python Unicode character index into unmodified JSONL page text", "lessons": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {len(lessons)} headings; preserved text at {len(lessons)-1} lecture boundaries")


if __name__ == "__main__":
    main()
