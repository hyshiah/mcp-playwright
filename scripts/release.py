#!/usr/bin/env python3
"""
发布脚本 - 自动化版本更新和标签创建
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_current_version() -> str:
    """获取当前版本号"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml 文件不存在")

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("无法从 pyproject.toml 中找到版本号")

    return match.group(1)


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """更新文件中的版本号"""
    content = file_path.read_text(encoding="utf-8")

    if file_path.name == "pyproject.toml":
        content = re.sub(
            r'version = "[^"]+"',
            f'version = "{new_version}"',
            content
        )
    elif file_path.name == "__init__.py":
        content = re.sub(
            r'__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content
        )

    file_path.write_text(content, encoding="utf-8")
    print(f"✅ 已更新 {file_path}")


def run_command(command: str) -> bool:
    """运行命令并返回是否成功"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {command}")
        print(f"错误输出: {e.stderr}")
        return False


def increment_version(version: str, part: str) -> str:
    """递增版本号"""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"版本号格式错误: {version}")

    major, minor, patch = map(int, parts)

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"未知的版本部分: {part}")

    return f"{major}.{minor}.{patch}"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/release.py <version|major|minor|patch>")
        print("示例:")
        print("  python scripts/release.py 0.2.0    # 设置特定版本")
        print("  python scripts/release.py patch     # 递增补丁版本")
        print("  python scripts/release.py minor     # 递增次版本")
        print("  python scripts/release.py major     # 递增主版本")
        sys.exit(1)

    version_arg = sys.argv[1]
    current_version = get_current_version()

    # 确定新版本号
    if version_arg in ["major", "minor", "patch"]:
        new_version = increment_version(current_version, version_arg)
    else:
        new_version = version_arg

    print(f"📦 当前版本: {current_version}")
    print(f"🚀 新版本: {new_version}")

    # 确认更新
    confirm = input("确认要更新版本并创建标签吗? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 取消发布")
        sys.exit(0)

    # 更新版本号
    pyproject_path = Path("pyproject.toml")
    init_path = Path("mcp_playwright/__init__.py")

    update_version_in_file(pyproject_path, current_version, new_version)
    update_version_in_file(init_path, current_version, new_version)

    # 运行测试
    print("🧪 运行测试...")
    if not run_command("uv run pytest tests/ -v"):
        print("❌ 测试失败，中止发布")
        sys.exit(1)

    # 构建包
    print("📦 构建包...")
    if not run_command("uv build"):
        print("❌ 构建失败，中止发布")
        sys.exit(1)

    # 提交更改
    print("💾 提交更改...")
    if not run_command(f"git add pyproject.toml mcp_playwright/__init__.py"):
        print("❌ Git 添加失败")
        sys.exit(1)

    if not run_command(f'git commit -m "🔖 发布版本 v{new_version}"'):
        print("❌ Git 提交失败")
        sys.exit(1)

    # 创建标签
    print("🏷️ 创建标签...")
    if not run_command(f"git tag v{new_version}"):
        print("❌ 创建标签失败")
        sys.exit(1)

    # 推送到远程
    print("📡 推送到远程仓库...")
    if not run_command("git push origin main"):
        print("❌ 推送主分支失败")
        sys.exit(1)

    if not run_command(f"git push origin v{new_version}"):
        print("❌ 推送标签失败")
        sys.exit(1)

    print(f"🎉 版本 v{new_version} 发布成功!")
    print("GitHub Actions 将自动构建并发布到 PyPI")
    print("请查看: https://github.com/ma-pony/mcp-playwright/actions")


if __name__ == "__main__":
    main()
