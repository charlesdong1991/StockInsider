from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

__keywords__ = ["chinese stock", "visualization", "insight", "stock analysis", "python"]

setup(
    name="StockInsider",
    description="The Python implementation of an stock analysis and visualization tool.",
    long_description_content_type='text/markdown',
    long_description=long_description,
    version="0.0.10",
    author="Kaiqi Dong",
    url="https://github.com/charlesdong1991/StockInsider",
    author_email="kaiqidong1991@gmail.com",
    licnese="MIT License",
    keywords=__keywords__,
    packages=find_packages(exclude=["test*"]),
    install_requires=["numpy>=1.18.3", "plotly>=4.6.0", "pandas>=1.0.3", "requests>=2.23.0"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
)
