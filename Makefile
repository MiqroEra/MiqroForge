# MiqroForge 项目构建工具

.PHONY: help install install-dev build clean deps test lint format

# 默认目标
help:
	@echo "MiqroForge 项目构建工具"
	@echo ""
	@echo "可用命令:"
	@echo "  help        - 显示此帮助信息"
	@echo "  install     - 安装项目依赖"
	@echo "  install-dev - 安装开发依赖"
	@echo "  build       - 构建项目"
	@echo "  clean       - 清理构建文件"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 代码格式化"

# 安装项目依赖
install:
	@echo "正在安装项目依赖..."
	@pip install -e . --break-system-packages

# 安装开发依赖
install-dev:
	@echo "正在安装开发依赖..."
	@pip install -e ".[dev]"

# 构建项目
build:
	@echo "正在构建项目..."
	@python -m build

# 清理构建文件
clean:
	@echo "正在清理构建文件..."
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 运行测试
test: install-dev
	@echo "正在运行测试..."
	@python -m pytest tests/ -v

# 代码检查
lint: install-dev
	@echo "正在检查代码..."
	@flake8 scripts/ tests/
	@mypy scripts/ tests/

# 代码格式化
format: install-dev
	@echo "正在格式化代码..."
	@black scripts/ tests/
	@isort scripts/ tests/

# 开发环境设置
dev-setup: install-dev format lint
	@echo "开发环境设置完成！"
