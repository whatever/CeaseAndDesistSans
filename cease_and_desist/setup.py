"""
CeaseAndDesistSans

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name="cease_and_desist",
    version="0.4.20", 
    description="Generate CeaseAndDesistSans-Refular.woff2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/whatever/CeaseAndDesistSans",
    author="Matt <3",
    author_email="matt@worldshadowgovernment.com",
    keywords="font, cease, desist, sans-serif",  # Optional
    # package_dir={"": "cease_and_desist"},  # Optional
    packages=find_packages(where="cease_and_desist"),  # Required
    python_requires=">=3.7, <4",
    install_requires=required,

    # extras_require={  # Optional
    #     "dev": ["check-manifest"],
    #     "test": ["coverage"],
    # },
    # package_data={  # Optional
    #     "sample": ["package_data.dat"],
    # },
    # data_files=[("my_data", ["data/data_file"])],  # Optional
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:

    entry_points={  # Optional
        "console_scripts": [
            "generate-cease-and-desist-sans=cease_and_desist:main",
            "serve-cease-and-desist-sans=cease_and_desist.server:main",
        ],
    },

    # scripts=["scripts/generate-cease-and-desist-sans"],

    project_urls={
        # "Bug Reports": "https://github.com/pypa/sampleproject/issues",
        # "Funding": "https://donate.pypi.org",
        # "Say Thanks!": "http://saythanks.io/to/example",
        # "Source": "https://github.com/pypa/sampleproject/",
    },
)
