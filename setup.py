from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="Mobile Agents Simulator",
    version="0.0.1",
    author="Sébastien Ratel",
    author_email="sebastien.ratel@centrale-marseille.fr",
    description="A minimal simulator for mobile agents in graphs",
    keywords="mobile agents, simulator, distributed algorithms",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Natural Language :: English",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.8.8",
        "License :: Free for non-commercial use",
    ],
    install_requires=[
        'numpy',
        'networkx',
        'matplotlib',
        'scipy',
        'sphinxcontrib_napoleon',
        'sphinx_rtd_theme',
        'pydot',
        'pytest_mock'
    ],
)
