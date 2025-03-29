#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="pokemmo-auto",
    version="0.1.0",
    description="PokeMMO游戏自动化工具",
    author="User",
    author_email="user@example.com",
    url="https://github.com/user/pokemmo-auto",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "numpy",
        "pillow",
        "pyautogui",
        "pywin32",
        "paddlepaddle",
        "paddleocr",
        "pydub",
        "pygame",
        "keyboard",
    ],
    entry_points={
        'console_scripts': [
            'pokemmo-auto=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
) 