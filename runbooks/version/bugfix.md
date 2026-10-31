# Runbook：缺陷修复

## 适用场景

- 已确认是不改变产品规则的缺陷，需要完成修复、验证与收尾。
- 排查方法见[问题排查](../problems/troubleshooting.md)，修复层次与范围见[修复决策](../problems/fix-decision.md)，缺陷记录的文件形式见[版本文档结构](../docs/structure/version-docs-structure.md#缺陷修复-bugfix)。

## 前置读取

- [问题排查](../problems/troubleshooting.md)
- [修复决策](../problems/fix-decision.md)

## 规则

- 只修不改变产品规则与对外行为的缺陷；会改变产品规则或接口契约的走需求变动。
- 一次只修一个根因；同一根因引起的多处症状一并修，不同根因分开记录与验证。
- 先写失败用例再改代码；修复最小化，不扩展功能、不顺带重构。
- 修复方案未确认时写入版本 `open-questions.md`，不在缺陷记录里保留备选。
- 连续 3 次修复无效时停止打补丁，回到架构层面重新评估（见修复决策）。
- 修复完成并回写文档后删除缺陷目录；版本完成时 `bugfix/` 为空。

## 步骤

1. 确认缺陷边界：不改变产品规则与对外行为，不属于需求变动。
2. 按[问题排查](../problems/troubleshooting.md)稳定复现并确认根因；无法确认时先补诊断证据。
3. 按[修复决策](../problems/fix-decision.md)确定修复层次、修改端与范围。
4. 建立缺陷目录并按[版本文档结构](../docs/structure/version-docs-structure.md#缺陷修复-bugfix)写 `bugfix.md`，先写失败用例。
5. 实施单一修复，只改决策范围内的文件。
6. 按[补充测试与验证](../implementation/testing.md)验证失败用例与回归点，回写 `docs/current/product/`、`docs/current/technical/` 与版本基线。
7. 删除缺陷目录；未确认事项转入版本 `open-questions.md`。

## 验证

- 失败用例修复前失败、修复后通过，回归点全部通过。
- 修复范围与决策一致，无顺带重构。
- `bugfix.md` 的根因与修复方案和实际改动一致。
- 文档已回写，缺陷目录已删除，`open-questions.md` 无遗留条目。

## 相关

- [需求变动](requirement-change.md)
