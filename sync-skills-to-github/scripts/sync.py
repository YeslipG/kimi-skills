#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 D:/Kimi/Skills 下的 skill 目录同步到 GitHub 仓库根目录，并推送。

用法：
    python sync.py
    python sync.py --message "更新 purchase-order 技能"
    python sync.py --repo-root "D:/Kimi" --skills-dir "D:/Kimi/Skills"
"""

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_ROOT = Path("D:/Kimi")
DEFAULT_SKILLS_DIR = Path("D:/Kimi/Skills")


def run(cmd, cwd, check=True):
    """运行命令并返回输出。"""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)} (exit {result.returncode})")
    return result


def dir_differs(src: Path, dst: Path) -> bool:
    """递归比较两个目录是否有差异（文件增删改）。"""
    if not dst.exists():
        return True
    dc = filecmp.dircmp(str(src), str(dst))
    if dc.left_only or dc.right_only or dc.diff_files:
        return True
    for sub in dc.common_dirs:
        if dir_differs(src / sub, dst / sub):
            return True
    return False


def ensure_git_identity(repo_root: Path):
    """如果没有配置 user.name / user.email，使用默认配置。"""
    for key in ["user.name", "user.email"]:
        res = run(["git", "config", "--local", key], cwd=repo_root, check=False)
        if not res.stdout.strip():
            if key == "user.name":
                run(["git", "config", "--local", "user.name", "YeslipG"], cwd=repo_root)
            else:
                run(["git", "config", "--local", "user.email", "YeslipG@users.noreply.github.com"], cwd=repo_root)


def main():
    parser = argparse.ArgumentParser(description="同步 Skills 到 GitHub")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT, help="本地 Git 仓库根目录")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR, help="本地 Skills 源目录")
    parser.add_argument("--remote", default="origin", help="Git remote 名称")
    parser.add_argument("--branch", default="main", help="目标分支")
    parser.add_argument("--message", "-m", default="", help="提交信息，为空时自动生成")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    skills_dir = args.skills_dir.resolve()

    if not (repo_root / ".git").exists():
        print(f"错误：{repo_root} 不是 Git 仓库", file=sys.stderr)
        sys.exit(1)
    if not skills_dir.exists():
        print(f"错误：{skills_dir} 不存在", file=sys.stderr)
        sys.exit(1)

    ensure_git_identity(repo_root)

    # 拉取最新代码，避免冲突
    run(["git", "fetch", args.remote, args.branch], cwd=repo_root)
    # 如果本地有提交历史，则合并远程；否则 reset 到远程分支
    has_commits = run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=False).returncode == 0
    if has_commits:
        run(["git", "merge", f"{args.remote}/{args.branch}"], cwd=repo_root)
    else:
        run(["git", "reset", "--hard", f"{args.remote}/{args.branch}"], cwd=repo_root)

    # 遍历源 Skills 目录，只同步有变更的 skill
    skill_names = []
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        # 跳过隐藏目录和临时目录
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        src = entry
        dst = repo_root / entry.name
        if not dir_differs(src, dst):
            print(f"跳过（无变更）: {entry.name}")
            continue
        print(f"同步: {src} -> {dst}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        skill_names.append(entry.name)

    if not skill_names:
        print("没有需要同步的 skill")
        sys.exit(0)

    # 添加变更
    for name in skill_names:
        run(["git", "add", name], cwd=repo_root)

    # 检查是否有变更
    diff = run(["git", "diff", "--cached", "--stat"], cwd=repo_root, check=False)
    if not diff.stdout.strip():
        print("没有变更需要提交")
        sys.exit(0)

    # 提交信息
    message = args.message.strip()
    if not message:
        if len(skill_names) == 1:
            message = f"Update {skill_names[0]} skill"
        else:
            message = f"Update skills: {', '.join(skill_names)}"

    run(["git", "commit", "-m", message], cwd=repo_root)
    run(["git", "push", args.remote, args.branch], cwd=repo_root)

    print(f"\n已同步 {len(skill_names)} 个 skill 并推送到 {args.remote}/{args.branch}")
    for name in skill_names:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
