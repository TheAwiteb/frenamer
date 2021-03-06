from setuptools import setup, find_packages
import re

KEYWORD = ["frenamer", "renamer", "file_renamer", "file", "file renamer"]

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", encoding="utf-8") as require_file:
    requires = [require.strip() for require in require_file]

with open("frenamer/version.py", "r", encoding="utf-8") as f:
    version = re.search(
        r'^version\s*=\s*"(.*)".*$', f.read(), flags=re.MULTILINE
    ).group(1)

setup(
    name="frenamer",
    version=version,
    description="Rename and unrename all files in the directory, alphabetically or randomly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TheAwiteb",
    author_email="Awiteb@hotmail.com",
    url="https://github.com/TheAwiteb/frenamer",
    packages=find_packages(),
    license="MIT",
    keywords=KEYWORD,
    entry_points={"console_scripts": ["frenamer = frenamer.__main__:app"]},
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requires,
)
