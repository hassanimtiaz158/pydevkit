from setuptools import find_packages, setup


setup(
    name="pydevkit",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["click", "groq", "rich"],
    entry_points={
        "console_scripts": [
            "pydevkit=pydevkit.cli:cli",
        ],
    },
    python_requires=">=3.9",
)
