from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

includes = [
    "Quote-System",
]

setup(
    name="Quote-System",
    version="1.0.0",
    packages=find_namespace_packages(include=includes),
    description="Myproject",
    install_requires=[],
    entry_points="""
        [console_scripts]
        Quote-System-cli=Quote_System.cli:cli
    """,
)
