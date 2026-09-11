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
| `--dry-run` | 关 | 只预演：源目录扫描 + 复制，不 add/commit/push |

## 安全防线（重要，改动前请先读）

> **事故背景**：2026-08-05 的提交 `c0129b8` 把 `byted-web-search/.env`（含真实
> `WEB_SEARCH_API_KEY`）推送进了**公开**仓库 `YeslipG/kimi-skills`，直到
> 2026-09-11 才通过历史重写清除。
>
> **根因**：原实现是「`shutil.rmtree` + `copytree` 整目录复制 + `git add`」，
> 而 **`.gitignore` 对已经被 git 跟踪的文件完全无效** —— 仓库里虽然早就有
> `.env` 规则，文件照样被推。
>
> **教训**：删文件、重写历史都只是止损；**密钥一旦推送过，必须到服务商控制台
> 吊销并重新签发**。

脚本现有三道防线：

| # | 阶段 | 行为 |
|---|------|------|
| 0 | 源目录扫描 | 复制**之前**扫描 `--skills-dir` 全文，命中真密钥直接中止 |
| 1 | 复制过滤 | `copytree` 跳过 `.env`、`*.key`、`*.pem`、`*.pfx`、`secrets.json`、`id_rsa` 等敏感文件名，以及 `__pycache__`、`.venv`、`node_modules` 等目录 |
| 2 | 暂存区校验 | `git add` 后复查**暂存路径**与**文件内容**，发现敏感文件立刻中止 |

- 文档里的占位符（`your_key`、`<填入>`、`xxx`、`AKIA...EXAMPLE`）会被自动忽略，**不会误报**。
- 命中敏感信息时脚本以 **exit code 2** 退出，**不提交、不推送**，远程零变化。
- 唯一的白名单例外：`.env.example` / `.env.sample` / `.env.template` / `.env.dist`。

**正确做法**：密钥放环境变量或仓库外的文件里，不要放进 skill 目录。

## 工作流程

1. 检查仓库身份配置（`user.name` / `user.email`），未配置则使用 `YeslipG` / `YeslipG@users.noreply.github.com`。
2. **[阶段 0]** 扫描源目录 `--skills-dir`，发现疑似密钥则中止。
3. `git fetch` 远程分支。
4. 如果本地没有提交历史，`git reset --hard origin/main` 对齐远程；否则 `git pull`。
5. 遍历 `D:/Kimi/Skills/` 下的 skill 目录，逐个复制到仓库根目录（敏感文件被过滤）。
6. `git add` 每个 skill 目录。
7. **[阶段 2]** 校验暂存区路径与内容，发现敏感文件则中止。
8. 如无变更则退出。
9. 自动提交并 `git push origin main`。

## 使用方式

```bash
python <skill-path>/scripts/sync.py
```

自定义提交信息：

```bash
python <skill-path>/scripts/sync.py -m "优化 purchase-order-to-supplier-contract 排版"
```

先预演、确认不会误带敏感文件：

```bash
python <skill-path>/scripts/sync.py --dry-run
```

## 注意事项

- 只同步 `D:/Kimi/Skills/` 下非隐藏、非下划线开头的目录。
- 会用源目录**覆盖**仓库根目录下同名 skill 目录，请确认源目录是最新版本。
- 如果仓库根目录存在其他非 skill 文件，脚本不会触碰它们。
- 网络：本机直连 GitHub 大包传输会被重置，推送可走本地代理
  `git -c http.proxy=http://127.0.0.1:10808 push origin main`。
- 排查「某文件是否已被跟踪」：`git ls-files | grep -i env`。
  有输出说明还在跟踪，需 `git rm --cached <path>` 停止跟踪（保留本地文件）。
