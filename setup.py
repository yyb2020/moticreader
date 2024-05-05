# setup.py

from setuptools import setup, find_packages

setup(
    name='moticreader',
    version='0.1',
    packages=find_packages(),
    description='A package for managing Motic image',
    author='yyb',
    author_email='yyb2020123@163.com',
    install_requires=[
        'pillow', 
        "PIL",
        "numpy",
        "io",
        "tifffile",
        "olefile",
    ],
    python_requires='>=3.6',
)
