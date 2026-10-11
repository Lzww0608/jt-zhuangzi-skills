# JT叔叔的庄子 Skill

用JT叔叔（谭杰中）讲述的庄子，帮助理解自己的情绪、关系、工作选择、真实好恶与生活练习。默认充分阅读原文，允许慢和较多token；以《内七篇课程》的完整论证深入问题，《基本功》作体系和练法对照。

入口是 [SKILL.md](SKILL.md)。本文件夹本身就是完整技能，不需要原先的下载路径。

## 已纳入的材料

- 《庄子》内七篇课程（2012–2013）：1458页、94讲，包括《渔父》《达生》等补充篇章。
- 《庄子基本功》：128页扫描讲义，已逐页识别为可检索文本。
- 两份原PDF、逐页全文、81个阅读分块、课程目录、全篇思想/生活例子索引、四份逐页复核补充、功法前置网络、问题导航、思想总纲及本地检索工具。

第一轮顺序阅读后整理了276张心法卡和509条例子索引；第二轮独立重新逐页复核全部1586页（《基本功》128页另逐图核对），新增或细化878个导航入口，四份补充共约18万字符，补足思想、例子、旁枝和本人修正，并修复案例主体与阅读边界。两轮卡片是检索入口，同一主题的展开会分别保留，不等于互不重复的理论或独立故事。

完整保留约194万字的机器文本；扫描OCR和听打初稿均可能有错字，精确引文需回查原PDF。文本不是仅靠摘要或少数关键词重写出来的。

## 使用

在这个文件夹对应的对话中，可以直接说：

> 请阅读当前文件夹的 SKILL.md，充分使用JT叔叔的庄子来分析：我在工作里总想证明自己，被批评就很难受。

本次已注册到个人技能目录 `~/.agents/skills/jt-zhuangzi-skills`，该链接指向此文件夹。以后在新对话里通过 `$jt-zhuangzi-skills` 调用即可；如果当前应用尚未刷新技能列表，重新打开对话或重启应用后再调用。

需要在其他运行环境安装时，可复制整个文件夹，或保留位置并建立链接：

```bash
mkdir -p ~/.agents/skills
ln -s /Users/lzww/jt-zhuangzi-skills ~/.agents/skills/jt-zhuangzi-skills
```

如该名称已存在，先确认已有技能，不覆盖。重新打开需要使用的对话后，可说：

> 请用 $jt-zhuangzi-skills 帮我看这个问题。请充分读相关原文，可以慢一些，使用JT的例子，给我一个可以在生活中练的切入点。

首次新对话默认分批通读《基本功》及扫描校注，再读取全部课程思想地图、四份复核补充、两份讲义中的相关上下文。深入个人困惑时至少完整读最贴合的一讲，并追到必要承接、条件和修正；事件描述短也适用。同一对话已读的内容可以复用。阅读深度和最终回答长度是两回事，你可以要求回答短些而仍充分阅读。

2026-10-11针对“引用有了，分析仍浅”的反馈，另补了[深入分析规程](references/depth/analysis-method.md)和[课程机制细读](references/depth/course-work-mechanisms.md)：要求重建原文怎样走到结论、对照具体心理片刻、让实际事实能够修正判断，再选对应的练习。并用转正谈话及四个变体做定向比较。可以直接对比[用户提供的原回答](checks/depth-baseline.md)与[转正案例修订示范](checks/promotion-depth-example.md)。充分收录和充分解释分开检验，不以引文数量证明深度。

## 回查资料

- [思想总纲](references/foundations.md)
- [完整思想结构与功法次序](references/source-architecture.md)
- [94讲目录](references/course-catalog.md)
- [个人问题导航](references/problem-routing.md)
- [基本功全篇索引](references/maps/jibengong.md)
- [课程早段](references/maps/course-early.md) · [课程中段](references/maps/course-middle.md) · [课程后段](references/maps/course-late.md)
- [逐页第二轮复核与四份补充](references/review/index.md) · [最终完整复核报告](checks/complete-review.md)
- [阅读、页码与OCR说明](references/reading-method.md)
- [深入分析规程](references/depth/analysis-method.md) · [工作评价、代偿与愿景的课程细读](references/depth/course-work-mechanisms.md)
- [创建与实际试用验证](checks/validation.md) · [工作问题回答示例](checks/work-example.md) · [亲情问题回答示例](checks/family-example.md)
- [本轮深度修订与验证](checks/depth-revision.md) · [独立评审](checks/depth-evaluation.md) · [转正问题修订示范](checks/promotion-depth-example.md)

技能会区分JT原有解释、原例与针对你的推论。玄学语言保留其体系含义；反省、真小人、支离其德会和自责、天然同理心、具体条件一起理解。

## 本地检索

只需要Python 3，无网络服务或额外检索依赖：

```bash
python3 scripts/jt_reader.py search --query '环中 反省 自责' --top 12
python3 scripts/jt_reader.py guide --query '小丹 还虚 琴心 集虚' --top 12
python3 scripts/jt_reader.py read --source jibengong --pages 81-86,109-113
python3 scripts/jt_reader.py verify
```

检索结果只是入口；技能必须再读完整页和上下文。原PDF校验值、页数和分块清单见 [manifest.json](references/corpus/manifest.json)。
