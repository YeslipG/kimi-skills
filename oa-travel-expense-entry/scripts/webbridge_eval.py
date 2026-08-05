#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
webbridge_eval.py — 通过 kimi-webbridge 在当前页面执行 JS，中文安全。

为什么需要它：在 Windows Git Bash 下用 curl -d 直接提交含中文的 JSON，
中文字节经常在传输链路上被损坏（变成 "��" 写入表单）。
本脚本用 json.dumps(ensure_ascii=True) 把非 ASCII 字符转成 \\uXXXX 转义，
纯 ASCII 传输，彻底避免乱码。

用法：
  python webbridge_eval.py <session> <js文件>      # 执行文件里的 JS
  echo 'JS代码' | python webbridge_eval.py <session>   # 从 stdin 读

JS 返回值会被原样打印（JSON 字符串会美化输出）。
"""
import sys, json, urllib.request

def ev(session, code):
    payload = {"action": "evaluate", "args": {"code": code}, "session": session}
    data = json.dumps(payload, ensure_ascii=True).encode("ascii")
    req = urllib.request.Request("http://127.0.0.1:10086/command", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8"))
    if not d.get("ok"):
        print("ERROR:", json.dumps(d, ensure_ascii=False)[:800]); sys.exit(1)
    v = d["data"].get("value")
    try:
        print(json.dumps(json.loads(v), ensure_ascii=False, indent=1))
    except (TypeError, json.JSONDecodeError):
        print(v)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    session = sys.argv[1]
    code = open(sys.argv[2], encoding="utf-8").read() if len(sys.argv) > 2 else sys.stdin.read()
    ev(session, code)
