from setuptools import setup, find_packages

setup(
    name="myviz",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "bokeh"
    ],
)
