#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HaiFeng
# @Email   : 24918700@qq.com
# @Time    : 2018/11/28
# @desc    : publish to PYPI


from setuptools import setup
import os

this_directory = os.path.abspath(os.path.dirname(__file__))


# 读取文件内容
def read_file(filename):
    with open(os.path.join(this_directory, filename), encoding='utf-8') as f:
        desc = f.read()
    return desc


# 获取依赖
def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


long_description = read_file('README.md')
long_description_content_type = "text/markdown",  # 指定包文档格式为markdown

os.system('pipreqs . --encoding=utf8 --force')  # 生成 requirements.txt

setup(
    name='work_weixin',  # 包名
    python_requires='>=3.4.0',  # python环境
    version='0.0.2.1',  # 包的版本
    description="企业微信开发接口",  # 包简介，显示在PyPI上
    long_description=long_description,  # 读取的Readme文档内容
    long_description_content_type=long_description_content_type,  # 指定包文档格式为markdown
    author="HaiFeng",  # 作者相关信息
    author_email='haifengat@vip.qq.com',
    url='https://github.com/haifengat/work_weixin',
    # 指定包信息，还可以用find_packages()函数
    # packages=find_packages(),
    packages=['work_weixin'],
    install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    include_package_data=True,
    license="MIT License",
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
