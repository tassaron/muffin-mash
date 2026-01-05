from setuptools import setup, find_packages
from os import path
from mash import __version__


try:
    this_location = path.abspath(path.dirname(__file__))
    with open(path.join(this_location, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    raise FileNotFoundError("The file `README.md` could not be found or accessed")

setup(
    name="mash",
    author="Brianna Rainey <tassaron.com>",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mistune",
    ],
    url="https://tassaron.com/code/muffin-mash",
    license="GPL-3.0-only",
    description="simple website generator: markdown as static html",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "markdown",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
    ],
    entry_points={
        "console_scripts": ["mash = mash.__main__:main"],
    },
)
