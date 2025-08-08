#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# 读取 README 文件作为长描述
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "MiqroForge 计算集群管理命令行工具"

setup(
    name="miqroforge",
    version="0.1.0",
    author="MiqroForge Team",
    author_email="team@miqroforge.com",
    description="MiqroForge 计算集群管理命令行工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/miqroforge/miqroforge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 基本依赖，可以根据实际需求添加
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8',
            'mypy',
        ],
    },
    entry_points={
        'console_scripts': [
            'miqroforge=miqroforge.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
