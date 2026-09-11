#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 D:/Kimi/Skills 下的 skill 目录同步到 GitHub 仓库根目录，并推送。

用法：
    python sync.py
    python sync.py --message "更新 purchase-order 技能"
    python sync.py --repo-root "D:/Kimi" --skills-dir "D:/Kimi/Skills"
    python sync.py --dry-run          # 只预演，不 add/commit/push

安全加固（2026-09-11）：
    起因：byted-web-search/.env（含 API Key）曾随目录复制进入仓库并推送到
    公开仓库 kimi-skills。原实现直接 shutil.copytree + git add，
    而 .gitignore 对「已跟踪文件」无效，导致密钥长期留在公开历史里。

    本版加入三道防线：
      1. 复制阶段：跳过敏感文件名（.env / *.key / *.pem / secrets.json ...）
         以及 __pycache__ / .venv / node_modules 等垃圾目录。
      2. 内容扫描：对即将提交的文件做密钥特征扫描，命中就中止。
      3. 提交前校验：git add 后检查暂存区路径与内容，出现敏感文件立刻中止。
"""

import argparse
import filecmp
import fnmatch
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 让中文输出在 GBK 控制台下也不炸
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass


DEFAULT_REPO_ROOT = Path("D:/Kimi")
DEFAULT_SKILLS_DIR = Path("D:/Kimi/Skills")

# ---------------------------------------------------------------- 安全规则

# 这些文件名（不区分大小写，按 basename 匹配）永不复制、永不提交
SENSITIVE_NAME_PATTERNS = [
    ".env", ".env.*", "*.env",
    "*.pem", "*.key", "*.pfx", "*.p12", "*.jks", "*.keystore", "*.ppk",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    "secrets.json", "credentials.json", "service-account.json",
    ".netrc", ".npmrc", ".pypirc", ".htpasswd",
]

# 复制时一并跳过的目录
IGNORE_DIR_NAMES = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode",
}

# 这些文件名属于「模板」，允许通过
SENSITIVE_ALLOWLIST = {
    ".env.example", ".env.sample", ".env.template", ".env.dist",
}

# 占位符特征：命中的片段里若含这些词，视为文档示例而非真密钥
PLACEHOLDER_HINTS = (
    "your_key", "yourkey", "your-key", "your_api", "api_key_here", "key_here",
    "xxx", "yyy", "zzz", "changeme", "change_me", "placeholder", "example",
    "sample", "dummy", "fake", "todo", "redacted", "****",
    "<", ">", "您", "你的", "填入", "复制", "在这里", "替换",
)

# 内容特征：命中即判定为疑似密钥
SECRET_CONTENT_PATTERNS = [
    (re.compile(r"WEB_SEARCH_API_KEY\s*=\s*['\"]?([A-Za-z0-9_\-]{16,})"), "WEB_SEARCH_API_KEY 赋值"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "OpenAI 风格 sk- 密钥"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key ID"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"), "GitHub 个人访问令牌"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "GitHub 细粒度令牌"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "Google API Key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"), "Slack Token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "私钥文件内容"),
    (re.compile(r"(?i)(?<![A-Za-z0-9])(api[_\-]?key|secret[_\-]?key|access[_\-]?key(_id)?|client[_\-]?secret|private[_\-]?key|access[_\-]?token|auth[_\-]?token|password|passwd)\s*[:=]\s*['\"]?([A-Za-z0-9/+=_\-]{16,})"),
     "通用密钥赋值"),
]

# 扫描内容时跳过的扩展名（二进制/大文件）
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".pdf",
    ".zip", ".7z", ".rar", ".gz", ".tar", ".whl", ".exe", ".dll", ".so",
    ".pyc", ".pyo", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov",
}
MAX_SCAN_BYTES = 2 * 1024 * 1024


def is_sensitive_name(name: str) -> bool:
    """文件名是否属于敏感文件（.env.example 等模板除外）。"""
    low = name.lower()
    if low in SENSITIVE_ALLOWLIST:
        return False
    return any(fnmatch.fnmatch(low, pat) for pat in SENSITIVE_NAME_PATTERNS)


def is_sensitive_path(rel_path: str) -> bool:
    """仓库内相对路径是否包含敏感文件片段。"""
    parts = Path(rel_path).parts
    return any(is_sensitive_name(p) for p in parts)


def copytree_ignore(dirpath, names):
    """shutil.copytree 的 ignore 回调：丢弃敏感文件与垃圾目录。"""
    ignored = []
    for n in names:
        if n in IGNORE_DIR_NAMES or is_sensitive_name(n):
            ignored.append(n)
    return ignored


def scan_text_for_secrets(text: str):
    """返回命中的特征描述列表（自动跳过文档里的占位符示例）。

    占位符判断只看「值」——如果正则带捕获组就取最后一个捕获组，
    避免变量名里出现 example/test 之类的词就漏判。
    """
    hits = []
    for pat, desc in SECRET_CONTENT_PATTERNS:
        for m in pat.finditer(text):
            # 有捕获组 -> 用最后一个捕获组（即密钥值本身）；否则用整体匹配
            value = m.group(m.lastindex) if (m.lastindex or 0) >= 1 else m.group(0)
            low = (value or "").lower()
            if any(h in low for h in PLACEHOLDER_HINTS):
                continue  # 文档示例（your_key / <填入> / xxx / AKIA...EXAMPLE），不是真密钥
            snippet = m.group(0)
            if len(snippet) > 60:
                snippet = snippet[:60] + "..."
            # 打码：只回显前 8 个字符
            hits.append(f"{desc} -> {snippet[:8]}***")
            break
    return hits


def scan_tree_for_secrets(root: Path):
    """扫描目录下所有文本文件，返回 [(相对路径, [命中描述])]。"""
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in BINARY_EXTS:
                continue
            if is_sensitive_name(fn):
                findings.append((str(p.relative_to(root)), ["敏感文件名（将被跳过，不会提交）"]))
                continue
            try:
                if p.stat().st_size > MAX_SCAN_BYTES:
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            hits = scan_text_for_secrets(text)
            if hits:
                findings.append((str(p.relative_to(root)), hits))
    return findings


# ---------------------------------------------------------------- git 辅助

def run(cmd, cwd, check=True):
    """运行命令并返回输出。"""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)} (exit {result.returncode})")
    return result


def dir_differs(src: Path, dst: Path) -> bool:
    """递归比较两个目录是否有差异（文件增删改），忽略敏感文件与垃圾目录。"""
    if not dst.exists():
        return True
    dc = filecmp.dircmp(str(src), str(dst), ignore=list(IGNORE_DIR_NAMES) + SENSITIVE_NAME_PATTERNS)
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


def abort(msg: str):
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("  已中止：检测到敏感信息，未做任何提交或推送", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(msg, file=sys.stderr)
    print("", file=sys.stderr)
    print("处理建议：", file=sys.stderr)
    print("  1. 把密钥移到环境变量或仓库外的文件里", file=sys.stderr)
    print("  2. 确认 .env 已在 .gitignore 中且未被 git 跟踪", file=sys.stderr)
    print("     git ls-files | grep -i env      # 有输出说明还在跟踪", file=sys.stderr)
    print("     git rm --cached <path>          # 停止跟踪但保留本地文件", file=sys.stderr)
    print("  3. 如果密钥曾经推送过，必须到服务商控制台吊销并重新签发", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- 主流程

def main():
    parser = argparse.ArgumentParser(description="同步 Skills 到 GitHub")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT, help="本地 Git 仓库根目录")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR, help="本地 Skills 源目录")
    parser.add_argument("--remote", default="origin", help="Git remote 名称")
    parser.add_argument("--branch", default="main", help="目标分支")
    parser.add_argument("--message", "-m", default="", help="提交信息，为空时自动生成")
    parser.add_argument("--dry-run", action="store_true", help="只预演：复制并扫描，但不 add/commit/push")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    skills_dir = args.skills_dir.resolve()

    if not (repo_root / ".git").exists():
        print(f"错误：{repo_root} 不是 Git 仓库", file=sys.stderr)
        sys.exit(1)
    if not skills_dir.exists():
        print(f"错误：{skills_dir} 不存在", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("  阶段 0：源目录密钥扫描（复制之前先拦一道）")
    print("=" * 70)
    src_findings = scan_tree_for_secrets(skills_dir)
    real_secrets = [(p, h) for p, h in src_findings if "敏感文件名" not in h[0]]
    skipped_files = [p for p, h in src_findings if "敏感文件名" in h[0]]

    if skipped_files:
        print(f"  将跳过 {len(skipped_files)} 个敏感文件（不复制、不提交）：")
        for p in skipped_files[:20]:
            print(f"    - {p}")
        if len(skipped_files) > 20:
            print(f"    ... 另有 {len(skipped_files) - 20} 个")
    if real_secrets:
        lines = "\n".join(f"  {p}\n      " + "\n      ".join(h) for p, h in real_secrets)
        abort(f"源目录中有文件内容疑似包含密钥：\n{lines}")
    if not skipped_files:
        print("  未发现敏感文件")

    ensure_git_identity(repo_root)

    # 拉取最新代码，避免冲突
    run(["git", "fetch", args.remote, args.branch], cwd=repo_root)
    has_commits = run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=False).returncode == 0
    if has_commits:
        run(["git", "merge", f"{args.remote}/{args.branch}"], cwd=repo_root)
    else:
        run(["git", "reset", "--hard", f"{args.remote}/{args.branch}"], cwd=repo_root)

    # 遍历源 Skills 目录，只同步有变更的 skill
    print("")
    print("=" * 70)
    print("  阶段 1：复制（敏感文件已被 copytree_ignore 排除）")
    print("=" * 70)
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
        shutil.copytree(src, dst, ignore=copytree_ignore)
        skill_names.append(entry.name)

    if not skill_names:
        print("没有需要同步的 skill")
        sys.exit(0)

    if args.dry_run:
        print("")
        print(f"[dry-run] 本应同步 {len(skill_names)} 个 skill：{', '.join(skill_names)}")
        print("[dry-run] 未执行 git add/commit/push")
        sys.exit(0)

    # 添加变更
    for name in skill_names:
        run(["git", "add", name], cwd=repo_root)

    # 防线 3：暂存区路径校验
    print("")
    print("=" * 70)
    print("  阶段 2：暂存区校验")
    print("=" * 70)
    staged = run(["git", "diff", "--cached", "--name-only"], cwd=repo_root, check=False).stdout.splitlines()
    staged = [s.strip() for s in staged if s.strip()]
    bad_paths = [p for p in staged if is_sensitive_path(p)]
    if bad_paths:
        abort("暂存区出现敏感文件路径：\n" + "\n".join(f"  {p}" for p in bad_paths))

    # 防线 3b：暂存区内容扫描
    content_hits = []
    for p in staged:
        full = repo_root / p
        if not full.is_file() or full.suffix.lower() in BINARY_EXTS:
            continue
        try:
            if full.stat().st_size > MAX_SCAN_BYTES:
                continue
            hits = scan_text_for_secrets(full.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        if hits:
            content_hits.append((p, hits))
    if content_hits:
        abort("暂存文件内容疑似包含密钥：\n" +
              "\n".join(f"  {p}\n      " + "\n      ".join(h) for p, h in content_hits))

    print(f"  暂存 {len(staged)} 个文件，路径与内容校验通过")

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
