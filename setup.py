import os.path
from typing import Dict, Type

import setuptools


MODULE_NAME = "elasticsearch-faker"
REPOSITORY_URL = f"https://github.com/thombashi/{MODULE_NAME:s}"
REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

pkg_info: Dict[str, str] = {}


def get_release_command_class() -> Dict[str, Type[setuptools.Command]]:
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


with open(os.path.join(MODULE_NAME.replace("-", "_"), "__version__.py")) as f:
    exec(f.read(), pkg_info)

with open("README.rst", encoding=ENCODING) as f:
    LONG_DESCRIPTION = f.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    INSTALL_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES = [line.strip() for line in f if line.strip()]

build_exe_requires = ["pyinstaller>=5.10.1", "text-unidecode"]

setuptools.setup(
    name=MODULE_NAME,
    version=pkg_info["__version__"],
    url=REPOSITORY_URL,
    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description="elasticsearch-faker is a CLI tool to generate fake data for Elasticsearch.",
    include_package_data=True,
    keywords=["elasticsearch", "faker"],
    license=pkg_info["__license__"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(exclude=["tests*"]),
    project_urls={
        "Source": REPOSITORY_URL,
        "Tracker": f"{REPOSITORY_URL:s}/issues",
    },
    python_requires=">=3.7",
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "buildexe": build_exe_requires,
        "es8": ["elasticsearch>=8,<9"],
        "test": TESTS_REQUIRES,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Terminals",
    ],
    cmdclass=get_release_command_class(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "elasticsearch-faker=elasticsearch_faker.__main__:cmd",
        ]
    },
)
