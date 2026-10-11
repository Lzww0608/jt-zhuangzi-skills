# 逐页第二轮复核：补充内容与回查入口

这个目录的四份补充是技能思想与案例导航的组成部分，默认首次使用需全部读完；不是仅用于检查的开发记录。仍须从导航回读原页，不将卡片释义冒充JT原话。

| 来源范围 | 补充导航 | 逐页台账 | 复核说明 |
|---|---|---|---|
| 课程1–480页 | [早段补充](early-supplement.md) | [早段台账](early-page-ledger.json) | [早段复核记录](../../checks/review-early.md) |
| 课程481–960页 | [中段补充](middle-supplement.md) | [中段台账](middle-page-ledger.json) | [中段复核记录](../../checks/review-middle.md) |
| 课程961–1458页 | [后段补充](late-supplement.md) | [后段台账](late-page-ledger.json) | [后段复核记录](../../checks/review-late.md) |
| 基本功1–128页 | [扫描复核补充](jibengong-supplement.md) | [逐页扫描台账](jibengong-page-ledger.json) | [扫描复核说明](../../checks/review-jibengong.md) |

[思想全貌与功法次序](../source-architecture.md)把各补充接回本体、日常练法、前置、境界与外挂；[个人问题导航](../problem-routing.md)供选入手方向。[OCR校读补注](../corpus/ocr-corrections.json)与原机器识别分开保存，逐页读取自动显示并纳入检索。

复核从原始逐页全文重新顺读，不把原地图的read=true当已完成；每页分别记主题、原例、由哪个旧卡或新卡覆盖、准确性或限界，扫描本再每页对照图像。本轮两来源1586页台账已连续齐全；《基本功》128页均已对照原扫描。后段分两人顺读并合并，独占尾段工作文件保留供审计，默认四份补充的后段正文已包含它，不需再重复读取。实际覆盖状态以台账和审核报告为准，不以目录标题里的范围代替完成数。

可运行`python3 scripts/audit_package.py`检查两PDF校验、1586页/81块、94讲共享页正文无漏/无重复、逐页复核记录与入口、扫描校注及内部链接。内容是否充分仍依赖逐页比对，这些机械检查不能宣称语义永无遗漏。

[最终完整复核报告](../../checks/complete-review.md)记录来源、878个新增/细化入口、48条扫描校注、全部执行检查及原稿自带缺文；[统计快照](../../checks/review-stats.json)含四份补充的字符数和校验值。

## 本轮已经落实的实质修复

- 原按下一讲起页减一会漏共享页的前讲尾段；现按94个原标题的页内位置切分。第4讲保留52页尾句，第1讲保留14页剩余段落；94讲拼接覆盖正文一次，无丢字/重复。
- 《基本功》128页逐页原扫描核读，关键词小丹、被动周天、攖宁、不退转、还虚、主客/物我两忘等追加已核补注；原OCR保留，避免掩盖提取状态。
- 第一轮地图未充分暴露的宗教译读、医学/内功世界观、文学旁枝、笑话后半段、限定与本人改口补入四份导航；既有卡准确的只登记覆盖，不把重复叙述膨胀为新理论。
- 新`guide`命令可检索第一轮地图与第二轮补充，返回文件、行号、标题，明确是导航；再用`search/read`回到源页。

## 查找方式

```bash
python3 scripts/jt_reader.py guide --query '小丹 三花聚顶 还虚' --source jibengong --top 12
python3 scripts/jt_reader.py guide --query '疗愈密码 高桥信次 自动书写' --top 12
python3 scripts/jt_reader.py search --query '反省 自责 罪恶感' --source jibengong --top 12
python3 scripts/jt_reader.py read --source jibengong --pages 108-113
```

例子的完整故事、来源条件及转折仍在原文。卡数是新增或细化入口数；不等独立思想数、独立故事数，也不是精确逐字校勘承诺。
