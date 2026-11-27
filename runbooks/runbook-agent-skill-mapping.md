---
agent:
  effort: high
---

# Runbook：Runbook 与 Agent/Skill 映射

## 适用场景

- 新增、改名或删除 runbook 后，需要同步对应的 Claude Code 与 Codex agent，以及需要 skill 承载的入口。
- 调整 runbook 的思考强度、agent 命名、skill 判定或生成脚本。

## 前置读取

- [runbook 编写与维护](runbook.md)

## 规则

### 唯一事实源

- 每篇可执行 runbook 顶部必须有 `agent.effort` frontmatter，取值 `low`、`high`、`xhigh`；目录 `README.md` 与 `index.md` 不参与。
- 格式固定，键名与缩进不可变：

```yaml
---
agent:
  effort: high
---
```

- 强度按任务性质选择：`low` 用于规则明确、按固定命令或表格执行的机械任务；`xhigh` 用于需要跨文件推理、架构取舍或不可逆操作的判断；其余使用 `high`。
- 同一 runbook 只写一次强度；agent 定义、Codex TOML、索引与命令均不重复登记。

### 产物

- Claude Code：`agents/<name>.md`，插件安装后由 `agents/` 目录自动发现，调用名为 `yongchun:<name>`。
- Codex：`codex-agents/<name>.toml`，插件清单不支持 `agents` 字段，接入项目需把文件复制到项目 `.codex/agents/` 或 `~/.codex/agents/`。
- 两端产物均由 `scripts/generate_runbook_agents.py` 生成，不得手改；生成物随 runbook 一并提交。
- skill 薄壳由 `scripts/generate_runbook_skills.py` 生成，与 agent 同源，规则见下文「Skill 生成」。

### 命名与描述

- agent 名称取 runbook 路径去掉 `runbooks/` 与 `.md`、`/` 换成 `-`；basename 重名时保留父目录段（`server-runtime`、`client-runtime`）。
- 名称只含小写字母、数字与 `-`，不含 `:`；重复或非法名称由脚本报错退出。
- `description` 由 runbook 标题与「适用场景」首条组成，不另写一份；skill 复用同一描述。

### 生成与校验

- 生成：`python3 scripts/generate_runbook_agents.py`。
- 漂移检查：`python3 scripts/generate_runbook_agents.py --check`，与磁盘不一致时退出码 1。
- `python3 scripts/check-runbooks.py` 校验 frontmatter 完整性与生成物漂移，两项任一失败视为未完成。
- 生成物只读：改规则先改 runbook，再重新生成，不直接编辑 `agents/` 或 `codex-agents/`。

### Skill 判定

按内容特征判断是否生成 skill；标记写在 runbook frontmatter，不另建清单：

| 内容特征 | 结论 | 例子 |
| --- | --- | --- |
| 含脚本、钩子或固定命令序列，产出可执行结果 | 必须 skill 化 | `bugfix`、`new-api`、`version-release` |
| 无可执行脚本，但需要在用户未点名时由模型自动发现并进入固定流程 | 可 skill 化，按迁移批次决定 | `plan`、`requirement-change`、`ui-design` |
| 已由手写 skill 承载 | 不重复生成薄壳 | `worktree.md` → `worktree-guard`；`worktree-delivery.md` → `delivery-merge-queue` |
| 只约束写作与表述、只解释概念或只做约定 | 保持 runbook，不建 skill | `docs-writing`、`explanation`、`make.md`、`terminal-execution.md` |
| 维护文档、索引与目录说明 | 不参与 | `runbook.md`、`runbook-agent-skill-mapping.md`、`index.md`、`README.md` |

- 判定为必须或可选 skill 的 runbook，在 `agent.effort` 之后加 `skill.enabled: true`；未标记视为未迁移或不适用。
- 已有手写 skill 承载的 runbook 不重复生成、也不标记；生成器不提供额外排除逻辑，靠未标记控制。
- 标记是唯一事实源：不维护 skill 清单、不在命令或索引中重复登记。

### Skill 生成

- frontmatter 只接受 `true` / `false`，`skill` 块可省略，省略等价于 `enabled: false`：

```yaml
---
agent:
  effort: high
skill:
  enabled: true
---
```

- 生成的薄壳写在 `skills/runbooks/<name>/SKILL.md`，正文只做路由与执行契约，按相对路径 `../../../runbooks/<stem>.md` 指向 runbook，不复制规则。
- 生成：`python3 scripts/generate_runbook_skills.py`；漂移检查：`python3 scripts/generate_runbook_skills.py --check`，与磁盘不一致时退出码 1。
- 无启用项时视为通过，不要求 `skills/runbooks/` 存在；写入时只删除 `skills/runbooks/` 下带生成标记的多余薄壳，不触碰 `skills/worktree/` 与 `skills/delivery/` 的手写 skill。
- 首次生成 skill 时，两端插件清单 `.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json` 的 `skills` 数组同时加入 `./skills/runbooks/`；分组未声明时 `scripts/plugin_selfcheck.py` 报错。
- 当所有生成项被移除（例如全部 `skill.enabled` 回退），生成器会删除空的 `skills/runbooks/` 目录；此时必须同步从两端插件清单的 `skills` 数组移除 `./skills/runbooks/`，再运行 `python3 scripts/plugin_selfcheck.py` 确认分组已清理。
- 生成物只读：改规则先改 runbook，再运行生成器，不直接编辑 `skills/runbooks/` 下的 `SKILL.md`。

### 迁移顺序

按触发频率分批迁移，每批单独验证后再进入下一批：

1. 批次 1：`claude-commands/` 的 12 个命令各自第一个 `@` 引用的主 runbook，共 12 篇：`engineering/algorithm-design.md`、`version/bugfix.md`、`implementation/change-delivery.md`、`docs/docs-restructure.md`、`product/feature-feasibility.md`、`product/feature-requirements.md`、`product/product-init.md`、`engineering/server/new-api.md`、`version/plan.md`、`delivery/version-release.md`、`delivery/server-deploy.md`、`product/ui/ui-design.md`。命令的次要引用是前置阅读，不随批次 1 生成。
2. 批次 2：[任务执行与交付](implementation/change-delivery.md)场景判定表中的其余 runbook。
3. 批次 3：其余判定为必须或可选 skill 的 runbook，按目录顺序。

每批完成标准：为对应 runbook 加 `skill.enabled: true` → 运行 `python3 scripts/generate_runbook_skills.py` → 首次生成时更新两端清单，并在 `README.md` 的 `skills/` 目录树中加入 `runbooks/` 条目 → `generate_runbook_skills.py --check`、`generate_runbook_agents.py --check`、`check-runbooks.py`、`plugin_selfcheck.py` 与测试全部通过。

## 步骤

1. 修改或新增 runbook，按规则写 `agent.effort`；判定为必须或可选 skill 的，再加 `skill.enabled: true`。
2. 运行 `python3 scripts/generate_runbook_agents.py` 重新生成两端产物。
3. 运行 `python3 scripts/generate_runbook_skills.py` 生成 skill 薄壳；首次生成时同步两端插件清单的 `skills` 数组，全部启用项移除时同步从两端清单删除 `./skills/runbooks/`。
4. 运行 `python3 scripts/generate_runbook_agents.py --check`、`python3 scripts/generate_runbook_skills.py --check`、`python3 scripts/check-runbooks.py` 与 `python3 scripts/plugin_selfcheck.py`，确认退出码为 0。
5. Codex 接入项目复制 TOML：`python3 scripts/generate_runbook_agents.py --install-codex <项目目录>`。
6. 同一任务提交 runbook、`agents/`、`codex-agents/` 与变更的 `skills/runbooks/`。

## 验证

- 每篇可执行 runbook 都有合法 `agent.effort`，README 与索引除外。
- 判定为必须或可选的 runbook 已标记 `skill.enabled: true`；手写 skill 承载项、维护文档、索引与纯规则文档未标记。
- `agents/` 与 `codex-agents/` 数量等于可执行 runbook 数量，无多余、无缺失；`skills/runbooks/` 只含启用项生成的薄壳。
- `generate_runbook_agents.py --check`、`generate_runbook_skills.py --check`、`check-runbooks.py`、`plugin_selfcheck.py` 与 `python3 -m unittest discover -s scripts -p 'test_*.py'` 退出码为 0。
- 无启用项时 `skills/runbooks/` 与两端插件清单中的 `./skills/runbooks/` 均不存在；有启用项时两端清单已声明该分组。
- 生成物中的名称、描述与强度与 runbook 一致，无手改痕迹；每篇启用项的 skill 与 runbook 一致，双端路径 `../../../runbooks/<stem>.md` 可用。

## 相关

- [全局索引](index.md)
- [Runbook 编写与维护](runbook.md)
