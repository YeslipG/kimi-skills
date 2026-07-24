---
name: sync-skills-to-github
description: 当 D:/Kimi/Skills 目录下的 skill 更新后，自动将其同步到 GitHub 仓库（kimi-skills）并推送。当用户说“把 skill 推到 GitHub”“同步 skills 到仓库”“更新后自动推送 skill”“skill 变更推送到 GitHub”或类似任务时触发。
---

# 同步 Skills 到 GitHub

## 功能说明
将 `D:/Kimi/Skills/` 下的 skill 目录（源目录）同步到本地 Git 仓库根目录，提交并推送到 GitHub。

## 触发条件
- “把 skill 推到 GitHub”
- “同步 skills 到仓库”
- “更新后自动推送 skill”
- “skill 变更推送到 GitHub”

## 默认配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--repo-root` | `D:/Kimi` | 本地 Git 仓库根目录，remote 指向 `kimi-skills` |
| `--skills-dir` | `D:/Kimi/Skills` | 本地 skill 源目录 |
| `--remote` | `origin` | Git remote 名称 |
| `--branch` | `main` | 目标分支 |
| `--message` / `-m` | 自动生成 | 提交信息 |

## 工作流程

1. 检查仓库身份配置（`user.name` / `user.email`），未配置则使用 `YeslipG` / `YeslipG@users.noreply.github.com`。
2. `git fetch` 远程分支。
3. 如果本地没有提交历史，`git reset --hard origin/main` 对齐远程；否则 `git pull`。
4. 遍历 `D:/Kimi/Skills/` 下的 skill 目录，逐个复制到仓库根目录。
5. `git add` 每个 skill 目录。
6. 如无变更则退出。
7. 自动提交并 `git push origin main`。

## 使用方式

```bash
python <skill-path>/scripts/sync.py
```

自定义提交信息：

```bash
python <skill-path>/scripts/sync.py -m "优化 purchase-order-to-supplier-contract 排版"
```

## 注意事项

- 只同步 `D:/Kimi/Skills/` 下非隐藏、非下划线开头的目录。
- 会用源目录**覆盖**仓库根目录下同名 skill 目录，请确认源目录是最新版本。
- 如果仓库根目录存在其他非 skill 文件，脚本不会触碰它们。
