from setuptools import setup, find_packages

setup(
    name="apex-cua",
    version="1.0.0",
    description="Sovereign Sub-Millisecond Native GUI Action Kernel & Computer-Use Hypervisor",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["apex_cua", "apex_cua.*"]),
    python_requires=">=3.9",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "apexcua=apex_cua.cli:main",
        ],
    },
)
