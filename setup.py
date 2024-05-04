# setup.py

from setuptools import setup, find_packages

setup(
    name='yybMotic',
    version='0.1',
    packages=find_packages(),
    description='A package for managing Motic image pyramids',
    author='yyb',
    author_email='your_email@example.com',
    install_requires=[
        'pillow',  # 如果你需要图像处理相关功能
    ],
    python_requires='>=3.6',
)
