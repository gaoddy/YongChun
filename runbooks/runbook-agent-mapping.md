---
agent:
  effort: high
---

# Runbook：Runbook 与 Agent 映射

## 适用场景

- 新增、改名或删除 runbook 后，需要同步对应的 Claude Code 与 Codex agent。
- 调整 runbook 的思考强度、agent 命名或生成脚本。

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

### 命名与描述

- agent 名称取 runbook 路径去掉 `runbooks/` 与 `.md`、`/` 换成 `-`；basename 重名时保留父目录段（`server-runtime`、`client-runtime`）。
- 名称只含小写字母、数字与 `-`，不含 `:`；重复或非法名称由脚本报错退出。
- `description` 由 runbook 标题与「适用场景」首条组成，不另写一份。

### 生成与校验

- 生成：`python3 scripts/generate_runbook_agents.py`。
- 漂移检查：`python3 scripts/generate_runbook_agents.py --check`，与磁盘不一致时退出码 1。
- `python3 scripts/check-runbooks.py` 校验 frontmatter 完整性与生成物漂移，两项任一失败视为未完成。
- 生成物只读：改规则先改 runbook，再重新生成，不直接编辑 `agents/` 或 `codex-agents/`。

## 步骤

1. 修改或新增 runbook，按规则写 `agent.effort`。
2. 运行 `python3 scripts/generate_runbook_agents.py` 重新生成两端产物。
3. 运行 `python3 scripts/generate_runbook_agents.py --check` 与 `python3 scripts/check-runbooks.py`，确认退出码为 0。
4. Codex 接入项目复制 TOML：`python3 scripts/generate_runbook_agents.py --install-codex <项目目录>`。
5. 同一任务提交 runbook、`agents/` 与 `codex-agents/` 的改动。

## 验证

- 每篇可执行 runbook 都有合法 `agent.effort`，README 与索引除外。
- `agents/` 与 `codex-agents/` 数量等于可执行 runbook 数量，无多余、无缺失。
- `--check` 与 `check-runbooks.py` 退出码为 0。
- 生成物中的名称、描述与强度与 runbook 一致，无手改痕迹。

## 相关

- [全局索引](index.md)
- [Runbook 编写与维护](runbook.md)
