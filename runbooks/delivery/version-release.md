---
agent:
  effort: xhigh
---

# Runbook：版本发布

## 适用场景

- 版本收尾后执行正式发版，完成合并 `main`、打 tag、发布产物与发版后核对。
- 本仓库插件的版本发布，以及已发布版本的回滚处理。
- 版本内容的开发与收尾见[版本开发](../version/version-development.md)；各端发布细节见[服务端发布](server-deploy.md)与[客户端发布](client-release.md)。

## 前置读取

- [任务执行与交付](../implementation/task-delivery.md)

## 发布判定

- 版本状态为「已完成」，`update/`、`bugfix/` 为空，文档已按[文档回写](../docs/docs-sync.md)更新。
- 验证矩阵全部通过，失败项已修复而非跳过或放宽断言。
- 版本记录、待打 tag 与产物使用同一版本号；任一处不一致时不进入发版。
- `open-questions.md` 中没有阻塞发版的待确认项；存在时先确认并写入承载它的文档。

## 发布顺序与版本号

- 先发布服务端，再发布客户端；客户端发布前确认其依赖的服务端版本已上线。
- 项目没有对应端时跳过该端，顺序只约束实际存在的端。
- 一次发版只对应一个版本号，发版过程中不修改。
- 同一版本号不重复发布；需要修正时提升版本号并重新发版。

## 分支与 Tag

- 开发阶段只提交并推送 `develop`；`main` 只在正式发版时更新。
- 将 `develop` 快进合并到 `main` 并推送：

```bash
git switch main
git merge --ff-only develop
git push origin main
```

- 无法快进时停止发版，排查 `develop` 与 `main` 的分叉；不改为普通合并，不压缩或改写历史。
- 发版点使用 annotated tag，名称与版本记录一致：

```bash
git tag -a v<版本> -m "v<版本>"
git push origin v<版本>
```

- 已推送的 tag 不移动、不删除、不复用；发版内容需要修正时提升版本号并新建 tag。

## 回滚

- 已发布版本出现问题时按端回滚：服务端按[服务端发布](server-deploy.md)回滚，客户端按[客户端发布](client-release.md)停止灰度或回退版本清单。
- 回滚不回退 `main`，不移动或删除 tag；修复通过新版本发布。

## 本仓库插件发版

- 版本号同时写入 `.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json` 的 `version`，并与版本记录一致。
- 发版前在仓库根目录运行：

```bash
python3 scripts/check-runbooks.py
python3 -m unittest discover -s skills/worktree-merge-queue-delivery/scripts
```

- 两个命令退出码均为 0 才进入发版；失败时修复后重跑，不放宽校验。
- 按「分支与 Tag」推送 `develop`、快进 `main` 并推送 tag；本仓库没有构建与产物上传步骤。
- tag 推送后，Claude Code 通过 GitHub marketplace `gaoddy/YongChun` 安装或更新，Codex 通过 `codex plugin marketplace add gaoddy/YongChun` 安装或更新到该版本。

## 步骤

1. 核对发布判定项：版本状态、`update/`、`bugfix/`、验证结果、待确认项与版本号。
2. 确定版本号并同步版本记录；本仓库同时同步两个插件清单的 `version`。
3. 先发布服务端，再发布客户端；本仓库跳过此步。
4. 在 `develop` 上完成发版提交并推送：`git push origin develop`。
5. 快进合并 `main` 并推送。
6. 创建 annotated tag 并推送。
7. 核对 `main` 指向、tag、版本记录与插件清单一致；本仓库运行校验命令。

## 验证

- `main` 是 `develop` 的快进结果，没有额外的合并提交或历史改写。
- tag `v<版本>` 已推送并指向发版提交，与版本记录、插件清单中的版本号一致。
- 服务端与客户端版本满足兼容要求，客户端最低支持版本已确认。
- 回滚路径在发版前已确认可执行。
- 本仓库的 `python3 scripts/check-runbooks.py` 与 skill 测试退出码为 0。

## 相关

- [版本开发](../version/version-development.md)
- [服务端发布](server-deploy.md)
- [客户端发布](client-release.md)
