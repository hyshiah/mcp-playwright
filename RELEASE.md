# 发布指南

本项目使用 GitHub Actions 自动化发布到 PyPI。

## 🚀 自动发布流程

### 1. 发布到 TestPyPI (测试)

每次推送到任何分支时，会自动发布到 TestPyPI：

```bash
# 推送代码，自动触发 TestPyPI 发布
git push origin main
```

### 2. 发布到正式 PyPI

当推送以 `v` 开头的标签时，会自动发布到正式 PyPI：

```bash
# 更新版本号
# 1. 在 pyproject.toml 中更新 version
# 2. 在 mcp_playwright/__init__.py 中更新 __version__

# 提交版本更新
git add pyproject.toml mcp_playwright/__init__.py
git commit -m "🔖 发布版本 v0.1.1"

# 创建并推送标签
git tag v0.1.1
git push origin v0.1.1

# 或者一键创建并推送标签
git tag v0.1.1 && git push origin v0.1.1
```

## 📋 发布前检查清单

- [ ] 更新 `pyproject.toml` 中的版本号
- [ ] 更新 `mcp_playwright/__init__.py` 中的 `__version__`
- [ ] 更新 `README.md` 中的变更说明
- [ ] 运行本地测试确保通过
- [ ] 检查 CI 状态确保所有测试通过

## 🔧 PyPI 配置

### 使用 Trusted Publisher (推荐)

本项目使用 GitHub Actions 的 Trusted Publisher 功能，无需手动配置 API 密钥。

1. 在 PyPI 上创建项目
2. 配置 Trusted Publisher：
   - 仓库所有者：`ma-pony`
   - 仓库名称：`mcp-playwright`
   - 工作流文件名：`publish.yml`
   - 环境名称：`pypi`

### 环境配置

在 GitHub 仓库设置中配置以下环境：

1. **pypi** 环境
   - 用于正式 PyPI 发布
   - 建议启用保护规则，仅允许 main 分支发布

2. **testpypi** 环境
   - 用于 TestPyPI 发布
   - 可以不设置保护规则

## 📦 发布的产物

每次发布会创建以下产物：

1. **Python 包**
   - 源码分发包 (`.tar.gz`)
   - Wheel 包 (`.whl`)

2. **GitHub Release**
   - 自动生成发布说明
   - 包含构建的包文件
   - 基于提交消息生成变更日志

## 🧪 本地测试发布

在正式发布前，可以本地测试构建过程：

```bash
# 安装构建依赖
uv sync --dev

# 清理旧的构建文件
rm -rf dist/

# 构建包
uv build

# 验证包
uv run twine check dist/*

# 测试安装
uv pip install dist/mcp_playwright-*.whl --force-reinstall

# 测试导入
python -c "import mcp_playwright; print(mcp_playwright.__version__)"
```

## 🔄 版本管理策略

我们使用 [语义版本](https://semver.org/lang/zh-CN/) 进行版本管理：

- **主版本号 (X.y.z)**：不兼容的 API 变更
- **次版本号 (x.Y.z)**：向下兼容的功能性新增
- **修订号 (x.y.Z)**：向下兼容的问题修正

### 版本号示例

- `v0.1.0` - 初始版本
- `v0.1.1` - Bug 修复
- `v0.2.0` - 新功能添加
- `v1.0.0` - 稳定版本发布

## 🚨 故障排除

### 发布失败常见问题

1. **版本号冲突**
   ```
   ERROR: File already exists.
   ```
   解决：确保版本号是新的，PyPI 不允许重复上传相同版本

2. **权限问题**
   ```
   ERROR: Invalid or non-existent authentication information.
   ```
   解决：检查 Trusted Publisher 配置或 API 密钥设置

3. **包验证失败**
   ```
   ERROR: Invalid distribution format.
   ```
   解决：检查 `pyproject.toml` 配置和包结构

### 手动发布 (紧急情况)

如果 GitHub Actions 发布失败，可以手动发布：

```bash
# 安装发布工具
uv add --dev twine

# 构建包
uv build

# 发布到 TestPyPI (测试)
uv run twine upload --repository testpypi dist/*

# 发布到正式 PyPI
uv run twine upload dist/*
```

## 📊 发布状态监控

可以通过以下方式监控发布状态：

1. **GitHub Actions** - 查看工作流执行状态
2. **PyPI 项目页面** - 确认包已成功上传
3. **GitHub Releases** - 检查发布说明是否正确生成

## 🔗 相关链接

- [PyPI 项目页面](https://pypi.org/project/mcp-playwright/)
- [TestPyPI 项目页面](https://test.pypi.org/project/mcp-playwright/)
- [GitHub Releases](https://github.com/ma-pony/mcp-playwright/releases)
- [GitHub Actions 工作流](https://github.com/ma-pony/mcp-playwright/actions)
