# MiqroForge 安装指南

## 从源码安装

### 方法一：pip 安装（推荐）

1. 克隆或下载源码到本地
2. 进入项目根目录
3. 安装包：

```bash
# 生产环境安装
pip install .

# 开发环境安装（可编辑模式）
pip install -e .

# 如果遇到外部管理环境错误，使用虚拟环境：
python3 -m venv miqroforge_env
source miqroforge_env/bin/activate  # Linux/Mac
# 或 miqroforge_env\Scripts\activate.bat  # Windows
pip install .
```

### 方法二：使用 setuptools

```bash
python setup.py install
```

## 安装验证

安装完成后，您可以在任何目录使用 `miqroforge` 命令：

```bash
# 查看帮助信息
miqroforge --help

# 查看计算节点
miqroforge show

# 查看节点状态
miqroforge status --detail

# 查看资源使用情况
miqroforge resources --live

# 提交任务
miqroforge task submit simulation-job.yaml

# 查看任务列表
miqroforge task list
```

## 卸载

```bash
pip uninstall miqroforge
```

## 开发环境设置

如果您要参与开发，建议安装开发依赖：

```bash
pip install -e ".[dev]"
```

这将安装以下开发工具：
- pytest (测试)
- black (代码格式化)
- flake8 (代码检查)
- mypy (类型检查)

## 系统要求

- Python 3.8 或更高版本
- 支持 Linux、macOS 和 Windows
