"""Behavioral checks for the actual portable corpus reader, using real source pages."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("jt_reader", ROOT / "scripts/jt_reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class ReaderTests(unittest.TestCase):
    def test_full_source_integrity(self):
        report = reader.verify()
        self.assertEqual(report["neiqipian"]["pages"], 1458)
        self.assertEqual(report["jibengong"]["pages"], 128)

    def test_simplified_query_finds_traditional_ocr(self):
        rows = reader.search("支离其德", source="jibengong", top=128)
        self.assertTrue(any(row["page"] == 113 for row in rows))
        self.assertTrue(any("支離其德" in row["matches"] for row in rows))

    def test_simplified_recognition_and_persuasion_find_their_source_pages(self):
        recognition = reader.search("认同", source="jibengong", top=128)
        persuasion = reader.search("说服", source="jibengong", top=128)
        self.assertTrue(any(row["page"] == 29 for row in recognition))
        self.assertTrue(any(row["page"] == 96 for row in persuasion))

    def test_ocr_annotations_remain_distinct_from_raw_text(self):
        notes = reader.correction_notes("jibengong", 120)
        self.assertTrue(any(n["verified"] == "止水心法" for n in notes))
        page = next(p for p in reader.load_pages("jibengong") if p["page"] == 120)
        self.assertIn("正水心法", page["text"])
        rows = reader.search("止水心法", source="jibengong")
        self.assertTrue(any(r["page"] == 120 for r in rows))

    def test_visual_corrections_recover_missing_stage_terms(self):
        for query, page in [("小丹", 90), ("撄宁", 108), ("不退转", 109), ("还虚", 119)]:
            rows = reader.search(query, source="jibengong", top=128)
            self.assertTrue(any(r["page"] == page for r in rows), (query, page))

    def test_guide_finds_new_details_and_retains_source_file(self):
        rows = reader.guide("小丹", source="jibengong", top=20)
        self.assertTrue(any(r["path"] == "references/review/jibengong-supplement.md"
                            and "BJ17" in r["heading"] for r in rows))
        self.assertTrue(all(r["evidence"] == "navigation_only" for r in rows))

    def test_pdf_wrap_does_not_hide_phrase(self):
        text, offsets = reader.indexed_normalize("他想說服\n別人相信他")
        term = "說服別人"
        start = text.index(term)
        self.assertEqual(offsets[start], 2)
        self.assertIn(term, text)

    def test_entire_lecture_keeps_tail_on_shared_boundary_page(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/jt_reader.py"), "read",
                                 "--source", "neiqipian", "--lesson", "4"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue("回家休息了，下礼拜再继续。" in result.stdout)
        self.assertNotIn("05 复习课", result.stdout)
        # The first lecture also has substantial text on the next title's page.
        first = subprocess.run([sys.executable, str(ROOT / "scripts/jt_reader.py"), "read",
                                "--source", "neiqipian", "--lesson", "1"], capture_output=True, text=True)
        self.assertTrue("我就觉得我宁愿什么都看不到" in reader.indexed_normalize(first.stdout)[0])
        self.assertNotIn("02 庄子的文学外包装纸", first.stdout)

    def test_entire_lecture_boundaries_match_source_headings(self):
        fourth = reader.lesson_range(4)
        self.assertEqual((fourth["start"], fourth["end"]), (40, 52))
        last = reader.lesson_range(94)
        self.assertEqual((last["start"], last["end"]), (1441, 1454))
        with self.assertRaises(ValueError):
            reader.lesson_range(95)

    def test_all_lecture_spans_cover_body_once_without_gaps(self):
        pages = {p["page"]: p["text"] for p in reader.load_pages("neiqipian")}
        actual = "".join(p["text"] for n in range(1, 95) for p in reader.lesson_pages(n))
        first = reader.lesson_range(1)
        expected = pages[6][first["start_offset"]:] + "".join(pages[n] for n in range(7, 1455))
        self.assertTrue(actual == expected, "Lecture spans discard or duplicate source text")

    def test_read_returns_full_pages_and_refuses_missing_pages(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/jt_reader.py"), "read",
                                 "--source", "neiqipian", "--pages", "43-44,148"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for p in reader.load_pages("neiqipian"):
            if p["page"] in {43, 44, 148}:
                self.assertIn(p["text"], result.stdout)
        invalid = subprocess.run([sys.executable, str(ROOT / "scripts/jt_reader.py"), "read",
                                  "--source", "jibengong", "--pages", "128-129"], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    unittest.main()
