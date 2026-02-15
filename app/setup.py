from setuptools import setup, find_packages

setup(
    name="adk-shared",
    version="0.1.0",
    packages=find_packages(exclude=["adk.*"]),
    install_requires=[
        "google-adk",
        "litellm",
    ],
)