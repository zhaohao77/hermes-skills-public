# -*- coding: utf-8 -*-
"""
scrapling-skill 环境安装脚本（自检+安装）
用法：python install_scrapling_env.py
- 自动检测各依赖是否就绪，发现缺失则立即安装
- 安装完成后验证可用性
- 全程用子进程验证，避免同进程 import 缓存问题
"""

import sys
import subprocess
import os
import time

# 强制 stdout/stderr 使用 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def run_and_stream(cmd):
    """执行命令并实时流式打印输出，返回 returncode"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        errors='replace'
    )
    for line in process.stdout:
        line = line.rstrip()
        if line:
            print(f"   {line}", flush=True)
    process.wait()
    return process.returncode


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


def verify_scrapling():
    """用子进程验证 scrapling 核心模块可正常导入"""
    code, _, stderr = run_silent([
        sys.executable, "-c",
        "from scrapling.fetchers import Fetcher, DynamicFetcher, StealthyFetcher; print('OK')"
    ])
    return code == 0, stderr


def main():
    start_time = time.time()

    print("=" * 52, flush=True)
    print("  scrapling-skill 环境安装", flush=True)
    print("=" * 52, flush=True)

    # ── 步骤 1/4：scrapling 包 ────────────────────────────
    print("\n[1/4] 检查 scrapling 包...", end=" ", flush=True)
    if check_package("scrapling"):
        print("✅ 已就绪，跳过", flush=True)
    else:
        print("❌ 未安装，开始安装...", flush=True)
        rc = run_and_stream([sys.executable, "-m", "pip", "install", "scrapling[all]"])
        if rc != 0:
            print("❌ scrapling 安装失败，请检查网络或手动执行：", flush=True)
            print("   pip install scrapling[all]", flush=True)
            sys.exit(1)
        print("✅ scrapling 安装完成", flush=True)

    # ── 步骤 2/4：playwright 包 ───────────────────────────
    print("\n[2/4] 检查 playwright 包...", end=" ", flush=True)
    if check_package("playwright"):
        print("✅ 已就绪，跳过", flush=True)
    else:
        print("❌ 未安装，开始安装...", flush=True)
        rc = run_and_stream([sys.executable, "-m", "pip", "install", "playwright==1.45.0"])
        if rc != 0:
            print("❌ playwright 安装失败，请检查网络或手动执行：", flush=True)
            print("   pip install playwright==1.45.0", flush=True)
            sys.exit(1)
        print("✅ playwright 安装完成", flush=True)

    # ── 步骤 3/4：playwright Chromium ────────────────────
    print("\n[3/4] 检查 playwright Chromium...", end=" ", flush=True)
    if check_playwright_chromium():
        print("✅ 已就绪，跳过", flush=True)
    else:
        print("❌ 未下载，开始下载...", flush=True)
        env = os.environ.copy()
        env["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright"
        process = subprocess.Popen(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        for line in process.stdout:
            line = line.rstrip()
            if line:
                print(f"   {line}", flush=True)
        process.wait()
        if process.returncode != 0:
            print("❌ playwright Chromium 下载失败", flush=True)
            print("💡 备选方案：", flush=True)
            print("   方案A：使用 Docker 模式：docker pull pyd4vinci/scrapling", flush=True)
            print("   方案B：手动重试：", flush=True)
            print("         set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright", flush=True)
            print("         python -m playwright install chromium", flush=True)
            sys.exit(1)
        print("✅ playwright Chromium 下载完成", flush=True)

    # ── 步骤 4/4：patchright Chromium ────────────────────
    print("\n[4/4] 检查 patchright Chromium...", end=" ", flush=True)
    if check_patchright_chromium():
        print("✅ 已就绪，跳过", flush=True)
    else:
        print("❌ 未下载，开始下载...", flush=True)
        env = os.environ.copy()
        env["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright"
        process = subprocess.Popen(
            [sys.executable, "-m", "patchright", "install", "chromium"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        for line in process.stdout:
            line = line.rstrip()
            if line:
                print(f"   {line}", flush=True)
        process.wait()
        if process.returncode != 0:
            print("❌ patchright Chromium 下载失败", flush=True)
            print("💡 备选方案：", flush=True)
            print("   方案A：使用 Docker 模式：docker pull pyd4vinci/scrapling", flush=True)
            print("   方案B：手动重试：", flush=True)
            print("         set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright", flush=True)
            print("         python -m patchright install chromium", flush=True)
            sys.exit(1)
        print("✅ patchright Chromium 下载完成", flush=True)

    # ── 最终验证 ─────────────────────────────────────────
    print("\n🔍 最终验证...", end=" ", flush=True)
    ok, err = verify_scrapling()
    if ok:
        elapsed = time.time() - start_time
        print("✅", flush=True)
        print(f"\n{'=' * 52}", flush=True)
        print(f"  ✅ 环境全部就绪，可以开始使用！（耗时 {elapsed:.1f} 秒）", flush=True)
        print(f"{'=' * 52}", flush=True)
    else:
        print("❌", flush=True)
        print(f"\n{'=' * 52}", flush=True)
        print("  ❌ 验证失败，scrapling 核心模块导入异常", flush=True)
        print(f"{'=' * 52}", flush=True)
        print(f"错误详情：{err.strip()}", flush=True)
        print("💡 建议：尝试重新运行本脚本，或手动执行：", flush=True)
        print("   pip install --force-reinstall scrapling[all]", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
