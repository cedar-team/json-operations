import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = "2.4.0"

setuptools.setup(
    name="json-operations",
    version=__version__,
    author="Cedar",
    author_email="",
    license="MIT",
    description="Specify function operations is JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cedar-team/json-operations",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    python_requires=">=3.6",
    install_requires=[],
    extras_require={"test": ["parameterized==0.8.1", "black==22.8.0", "isort==5.10.1"]},
)
