"""Setup configuration for Houdini Swap SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="houdiniswap-sdk",
    version="0.1.0",
    author="Houdini Swap SDK Contributors",
    author_email="sdk@houdiniswap.com",
    description="Python SDK for Houdini Swap API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/houdiniswap/houdiniswap-sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    license="MIT",
    keywords=["houdiniswap", "crypto", "exchange", "swap", "api", "sdk"],
    project_urls={
        "Bug Tracker": "https://github.com/houdiniswap/houdiniswap-sdk-python/issues",
        "Documentation": "https://github.com/houdiniswap/houdiniswap-sdk-python/blob/main/README.md",
        "Source Code": "https://github.com/houdiniswap/houdiniswap-sdk-python",
    },
    zip_safe=False,
    include_package_data=True,
)

