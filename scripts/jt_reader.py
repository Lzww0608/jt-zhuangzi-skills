#!/usr/bin/env python3
"""Portable, offline page search and reading. Python 3 standard library only."""
import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "references/corpus"
# These are retrieval equivalents, not claims of philosophical equivalence.
ALIASES = [
    "庄子 莊子", "基本功", "心力", "我执 我執 ego", "自我价值 自我價值",
    "情绪 情緒", "情绪独立 情緒獨立 宋荣子 宋榮子", "好恶 好惡 喜欢 喜歡",
    "逍遥游 逍遙遊", "齐物论 齊物論", "养生主 養生主", "人间世 人間世",
    "德充符", "大宗师 大宗師", "应帝王 應帝王", "渔父 漁父", "达生 達生",
    "虑叹 慮嘆 慮歎", "反省", "成心", "信念", "代偿 代償", "代偿反应 代償反應",
    "比较 比較", "批评 批評", "认可 認可", "争强 爭強", "输赢 輸贏", "面子",
    "控制", "不妥协 不妥協", "拯救 救世主", "受害者 被害者", "加害者",
    "虚舟 虛舟", "心斋 心齋", "坐忘", "气听 氣聽", "身体感 身體感", "后味 後味",
    "丧我 喪我 吾丧我 吾喪我", "知止", "道枢 道樞", "道通为一 道通為一",
    "庖丁", "因循", "无用 無用", "无用之用 無用之用", "支离其德 支離其德",
    "不材", "才全德不形", "长德忘形 長德忘形", "真人", "撄宁 攖寧 搜宁 搜寧", "安命",
    "死亡 生死 死生", "苦难 苦難", "爱 愛", "真爱 真愛", "亲密 親密",
    "婚姻", "伴侣 伴侶", "恋爱 戀愛", "父母", "婆媳", "教育", "愧疚 罪恶感 罪惡感",
    "道德", "做善事 做好人", "份位 分位", "名利", "成功", "患得患失",
    "呆若木鸡 呆若木雞 木鸡 木雞 斗鸡 鬥雞", "梓庆 梓慶", "忘我自适 忘我自適",
    "头脑 頭腦", "思考", "想象 想像", "投射 投影", "伤心 傷心", "愤怒 憤怒 生气 生氣",
    "焦虑 焦慮", "恐惧 恐懼", "忧郁 憂鬱 抑郁 抑鬱", "身体 身體", "疾病", "养生 養生",
    "牺牲 犧牲", "忍耐", "气密 氣密", "打通", "四患", "八疵", "体用 體用",
    "自责 自責", "正见 正見", "无情 無情", "可爱 可愛", "保始", "集虚 集虛",
    "心向内 心向內", "影响力 影響力", "无为 無為", "环中 環中", "冲虚 冲虛 沖虛",
    "冲和 沖和", "龙蛇 龍蛇", "龙蛇混杂 龍蛇混雜", "我搞错了 我搞錯了",
    "搞错 搞錯", "天然同理心", "人工罪恶感 人工罪惡感", "真小人", "借假修真",
    "明镜止水 明鏡止水", "份位 分位", "止水", "舍象 捨象", "白象", "后味 後味",
    "桥梁信念 橋梁信念 橋樑信念", "真力", "假力", "结构张力 結構張力",
    "感受基调 感受基調 feelingtone", "价值完成 價值完成", "琴心", "好恶分明 好惡分明",
    "认同 認同", "掌声 掌聲", "说服 說服", "证明 證明", "争辩 爭辯",
    "不实念波 不實念波", "念波", "自我辩论 自我辯論", "表面意识 表面意識",
    "潜在意识 潛在意識", "内在小孩 內在小孩", "内在呼唤 內在呼喚 innercalling",
    "我也会 我也會", "批判", "指责 指責", "委屈", "羞耻 羞恥", "责任 責任",
    "孝顺 孝順", "感谢 感謝", "乐趣 樂趣", "幸福", "挫败 挫敗", "自卑", "自豪",
    "不退转 不退轉", "还虚 還虛", "阴神 陰神", "阳神 陽神", "识神 識神", "元神",
    "三花聚顶 三花聚頂", "小丹 小药 小藥", "大药 大藥", "卯酉周天", "大周天", "小周天",
    "琴心三叠 琴心三疊 琴心三叠", "无缘同体 無緣同體", "天生天养 天生天養",
    "疗愈密码 療癒密碼 療愈密碼", "夏威夷大法", "高桥信次 高橋信次", "反信法",
    "心经 心經", "波旬", "无相天魔 無相天魔", "伪空 偽空", "隐形我执 隱形我執",
    "生命主轴 生命主軸", "矛盾代偿 矛盾代償", "幸福原則 幸福原则", "气密 氣密",
]


def normalize(s):
    return unicodedata.normalize("NFKC", s).casefold()


def indexed_normalize(s):
    """Ignore PDF line wraps, while preserving offsets into the original page."""
    pieces, offsets = [], []
    for index, char in enumerate(s):
        value = normalize(char)
        if not value.isspace():
            pieces.append(value)
            offsets.extend([index] * len(value))
    return "".join(pieces), offsets


def correction_notes(source, page):
    path = CORPUS / "ocr-corrections.json"
    if source != "jibengong" or not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [c for c in data["corrections"] if c["page"] == page]


def load_pages(source=None):
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    if source and source not in manifest["sources"]:
        raise ValueError(f"Unknown or unavailable source: {source}")
    for sid in ([source] if source else manifest["sources"]):
        path = CORPUS / sid / "pages.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def term_groups(query, expand=True):
    words = [w for w in re.split(r"[\s,，;；|]+", normalize(query)) if w]
    groups = []
    for word in words:
        equivalents = {word}
        if expand:
            for group in ALIASES:
                variants = {normalize(v) for v in group.split()}
                if word in variants:
                    equivalents.update(variants)
        groups.append(sorted(equivalents))
    return groups


def search(query, source=None, top=12, context=220, expand=True):
    groups = term_groups(query, expand)
    if not groups:
        raise ValueError("Provide at least one search term")
    rows = []
    for page in load_pages(source):
        raw = page["text"]
        notes = correction_notes(page["source"], page["page"])
        searchable = raw + "\n" + "\n".join(c["verified"] for c in notes)
        norm, offsets = indexed_normalize(searchable)
        matches = []
        score = 0.0
        positions = []
        for group in groups:
            present = [(term, norm.count(term)) for term in group if term in norm]
            if present:
                matches.extend(term for term, _ in present)
                score += 2 + math.log1p(sum(count for _, count in present))
                positions.extend(norm.find(term) for term, _ in present)
        if matches:
            # Reward distinct concepts, then repeated mentions. This is keyword retrieval.
            score += sum(any(term in norm for term in group) for group in groups) ** 2
            pos = offsets[min(positions)]
            preview = searchable[max(0, pos - context // 3):pos + context]
            if page["source"] == "neiqipian" and (page["page"] < 6 or page["page"] > 1454):
                score *= 0.15  # Front matter and credits are navigation, not argument evidence.
            rows.append({"source": page["source"], "page": page["page"], "score": round(score, 3),
                         "matches": sorted(set(matches)), "preview": preview,
                         "citation": f"{page['source']}:p{page['page']:04d}"})
    return sorted(rows, key=lambda r: (-r["score"], r["source"], r["page"]))[:top]


def guide(query, source=None, top=12, context=300, expand=True):
    """Search maps and second-pass supplements, keeping navigation separate from source evidence."""
    groups = term_groups(query, expand)
    if not groups:
        raise ValueError("Provide at least one search term")
    rows = []
    for directory in [ROOT / "references/maps", ROOT / "references/review"]:
        for path in sorted(directory.glob("*.md")):
            # Tail reviewers' working files are merged into the four canonical supplements.
            if directory.name == "review" and path.name not in {
                    "early-supplement.md", "middle-supplement.md", "late-supplement.md",
                    "jibengong-supplement.md"}:
                continue
            sid = "jibengong" if path.name.startswith("jibengong") else "neiqipian"
            if source and source != sid:
                continue
            raw = path.read_text(encoding="utf-8")
            headings = list(re.finditer(r"(?m)^(?:#{1,6} .+|(?:[-*] )?\*\*[^\n]+|\| [^\n]+)$", raw))
            for index, heading in enumerate(headings):
                end = headings[index + 1].start() if index + 1 < len(headings) else len(raw)
                block = raw[heading.start():end]
                norm, offsets = indexed_normalize(block)
                matches, positions, score, distinct = [], [], 0.0, 0
                for group in groups:
                    present = [(term, norm.count(term)) for term in group if term in norm]
                    if present:
                        distinct += 1
                        matches.extend(term for term, _ in present)
                        score += 2 + math.log1p(sum(count for _, count in present))
                        positions.extend(norm.find(term) for term, _ in present)
                if not matches:
                    continue
                pos = offsets[min(positions)]
                rows.append({"source": sid, "path": str(path.relative_to(ROOT)),
                             "line": raw.count("\n", 0, heading.start()) + 1,
                             "heading": heading.group().strip("#* "),
                             "score": round(score + distinct ** 2, 3),
                             "matches": sorted(set(matches)),
                             "preview": block[max(0, pos - context // 3):pos + context],
                             "evidence": "navigation_only"})
    return sorted(rows, key=lambda r: (-r["score"], r["path"], r["line"]))[:top]


def parse_pages(spec):
    result = set()
    for token in spec.split(","):
        if "-" in token:
            first, last = map(int, token.split("-", 1))
            if first < 1 or last < first:
                raise ValueError(f"Invalid range: {token}")
            result.update(range(first, last + 1))
        else:
            result.add(int(token))
    if not result or min(result) < 1:
        raise ValueError("Page numbers must be positive")
    return result


def lesson_range(number):
    lessons = json.loads((CORPUS / "lessons.json").read_text(encoding="utf-8"))
    for lesson in lessons:
        if lesson["number"] == number:
            return lesson
    raise ValueError(f"Unavailable lesson: {number}; valid range is 1-94")


def lesson_pages(number):
    """Complete lecture text, including its tail before the following page's title."""
    lesson = lesson_range(number)
    result = []
    for page in load_pages("neiqipian"):
        if lesson["start"] <= page["page"] <= lesson["end"]:
            first = lesson["start_offset"] if page["page"] == lesson["start"] else 0
            last = lesson["end_offset"] if page["page"] == lesson["end"] else len(page["text"])
            result.append({**page, "text": page["text"][first:last]})
    return result


def verify():
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    report = {}
    for sid, info in manifest["sources"].items():
        pages = list(load_pages(sid))
        assert [p["page"] for p in pages] == list(range(1, info["pages"] + 1)), f"Page coverage: {sid}"
        assert all(p["source"] == sid for p in pages), f"Source IDs: {sid}"
        assert hashlib.sha256((ROOT / info["pdf"]).read_bytes()).hexdigest() == info["sha256"], f"PDF checksum: {sid}"
        covered = []
        for c in info["chunks"]:
            text = (ROOT / c["path"]).read_text(encoding="utf-8")
            for number in range(c["start"], c["end"] + 1):
                assert text.count(f"## {sid}:p{number:04d}\n") == 1, f"Anchor missing: {sid} {number}"
                page = pages[number - 1]
                assert page["text"] in text, f"Page text mismatch: {sid} {number}"
            covered.extend(range(c["start"], c["end"] + 1))
        assert covered == list(range(1, info["pages"] + 1)), f"Chunk coverage: {sid}"
        assert sum(len(p["text"]) for p in pages) == info["characters"], f"Character count: {sid}"
        report[sid] = {"pages": len(pages), "characters": info["characters"], "chunks": len(info["chunks"]),
                       "empty_pages": info["empty_pages"], "sha256_ok": True}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text, context in [("search", "Source-page candidates; read full pages afterward", 220),
                                        ("guide", "Search maps and supplements; navigation only", 300)]:
        s = sub.add_parser(command, help=help_text)
        s.add_argument("--query", required=True)
        s.add_argument("--source", choices=["neiqipian", "jibengong"])
        s.add_argument("--top", type=int, default=12)
        s.add_argument("--context", type=int, default=context)
        s.add_argument("--exact", action="store_true", help="Disable retrieval aliases")
    r = sub.add_parser("read", help="Return complete pages; PDF page numbers, inclusive")
    r.add_argument("--source", required=True, choices=["neiqipian", "jibengong"])
    selection = r.add_mutually_exclusive_group(required=True)
    selection.add_argument("--pages", help="e.g. 43-46,148-150")
    selection.add_argument("--lesson", type=int, help="Entire neiqipian lecture, 1-94")
    sub.add_parser("verify", help="Check PDFs, page/chunk coverage, anchors, and text")
    sub.add_parser("catalog", help="Source metadata")
    args = parser.parse_args()
    try:
        if args.command in {"search", "guide"}:
            if args.top < 1 or args.context < 1:
                raise ValueError("--top and --context must be positive")
            operation = search if args.command == "search" else guide
            for row in operation(args.query, args.source, args.top, args.context, not args.exact):
                print(json.dumps(row, ensure_ascii=False))
        elif args.command == "read":
            if args.lesson is not None:
                if args.source != "neiqipian":
                    raise ValueError("--lesson is only available for neiqipian")
                lesson = lesson_range(args.lesson)
                selected = set(range(lesson["start"], lesson["end"] + 1))
                pages = lesson_pages(args.lesson)
            else:
                selected = parse_pages(args.pages)
                pages = [p for p in load_pages(args.source) if p["page"] in selected]
            missing = selected - {p["page"] for p in pages}
            if missing:
                raise ValueError(f"Unavailable pages: {sorted(missing)}")
            for page in pages:
                print(f"\n## {page['source']}:p{page['page']:04d}\n\n{page['text']}\n")
                for note in correction_notes(page["source"], page["page"]):
                    print(f"[扫描校读补注：OCR「{note['ocr']}」应读「{note['verified']}」。{note['note']}]\n")
        elif args.command == "verify":
            print(json.dumps(verify(), ensure_ascii=False, indent=2))
        else:
            manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
            for sid, info in manifest["sources"].items():
                print(json.dumps({"source": sid, **{k: v for k, v in info.items() if k != "chunks"}}, ensure_ascii=False))
    except (ValueError, AssertionError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
