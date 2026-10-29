# -*- coding: utf-8 -*-
"""
scrapling-skill 环境检测脚本（纯检测，不安装）
用法：python check_scrapling_env.py
- 快速检测各依赖是否就绪，约 2~5 秒返回
- 不做任何安装操作
- 如有缺失，输出预期安装时间供 AI 告知用户
- 安装请运行：python install_scrapling_env.py
"""

import sys
import subprocess
import os

# 强制 stdout/stderr 使用 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def run_silent(cmd):
    """静默执行命令，返回 (returncode, stdout, stderr)"""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.returncode, result.stdout, result.stderr


def check_package(package_name):
    code, _, _ = run_silent([sys.executable, "-c", f"import {package_name}"])
    return code == 0


def check_playwright_chromium():
    code, _, _ = run_silent([
        sys.executable, "-c",
        (
            "from playwright.sync_api import sync_playwright; "
            "p = sync_playwright().start(); "
            "path = p.chromium.executable_path; "
            "p.stop(); "
            "import os; exit(0 if os.path.exists(path) else 1)"
        )
    ])
    return code == 0


def check_patchright_chromium():
    code, _, _ = run_silent([
        sys.executable, "-c",
        (
            "from patchright.sync_api import sync_playwright; "
            "p = sync_playwright().start(); "
            "path = p.chromium.executable_path; "
            "p.stop(); "
            "import os; exit(0 if os.path.exists(path) else 1)"
        )
    ])
    return code == 0


def main():
    print("=" * 52, flush=True)
    print("  scrapling-skill 环境检测", flush=True)
    print("=" * 52, flush=True)

    missing = []

    # [1/4] scrapling 包
    print("\n[1/4] 检查 scrapling 包...", end=" ", flush=True)
    if check_package("scrapling"):
        print("✅ 已就绪", flush=True)
    else:
        print("❌ 未安装", flush=True)
        missing.append("scrapling")

    # [2/4] playwright 包
    print("[2/4] 检查 playwright 包...", end=" ", flush=True)
    if check_package("playwright"):
        print("✅ 已就绪", flush=True)
    else:
        print("❌ 未安装", flush=True)
        missing.append("playwright")

    # [3/4] playwright Chromium
    print("[3/4] 检查 playwright Chromium...", end=" ", flush=True)
    if check_playwright_chromium():
        print("✅ 已就绪", flush=True)
    else:
        print("❌ 未下载", flush=True)
        missing.append("playwright-chromium")

    # [4/4] patchright Chromium
    print("[4/4] 检查 patchright Chromium...", end=" ", flush=True)
    if check_patchright_chromium():
        print("✅ 已就绪", flush=True)
    else:
        print("❌ 未下载", flush=True)
        missing.append("patchright-chromium")

    # 汇总
    print(flush=True)
    if not missing:
        print("✅ 环境全部就绪，可以直接开始使用。", flush=True)
    else:
        print(f"⚠️  发现 {len(missing)} 项未就绪：{', '.join(missing)}", flush=True)
        # 估算时间：供 AI 读取后告知用户
        minutes = 0
        if "scrapling" in missing:
            minutes += 2
        if "playwright" in missing:
            minutes += 1
        if "playwright-chromium" in missing:
            minutes += 5
        if "patchright-chromium" in missing:
            minutes += 5
        print(f"⏱  预计安装时间：约 {minutes} 分钟", flush=True)
        print("➡️  请运行安装脚本：python install_scrapling_env.py", flush=True)


if __name__ == "__main__":
    main()
