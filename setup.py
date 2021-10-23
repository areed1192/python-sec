from setuptools import setup
from setuptools import find_namespace_packages

# load the README file.
with open(file="README.md", mode="r") as readme_file:
    long_description = readme_file.read()

setup(

    # this will be my Library name.
    name='python-sec',

    # Want to make sure people know who made it.
    author='Alex Reed',

    # also an email they can use to reach out.
    author_email='coding.sigma@gmail.com',

    # define the version of the package.
    version='0.1.5',

    # here is a simple description of the library, this will appear when someone
    # searches for the library on https://pypi.org/search
    description='A client library for collecting and scraping SEC filings.',

    # I have a long description but that will just be my README file, note the
    # variable up above where I read the file.
    long_description=long_description,

    # want to make sure that I specify the long description as MARKDOWN.
    long_description_content_type="text/markdown",

    # here is the URL you can find the code, this is just the GitHub URL.
    url='https://github.com/areed1192/python-sec',

    # there are some dependencies to use the library, so let's list them out.
    install_requires=[
        'requests==2.25.1',
        'urllib3==1.26.5',
        'beautifulsoup4==4.9.1'
    ],

    # some keywords for my library.
    keywords='finance, sec, api, web scraping, financial disclosures',

    # here are the packages I want "build."
    packages=find_namespace_packages(
        include=['edgar', 'samples', 'tests']
    ),

    package_dir={
        "": ".",
        "samples": ".",
        "tests": "."
    },

    # here we specify any package data.
    package_data={
        "edgar": ["parsing/*"],
    },

    # I also have some package data, like photos and JSON files, so I want to include those too.
    include_package_data=True,

    # additional classifiers that give some characteristics about the package.
    classifiers=[

        # I want people to know it's still early stages.
        'Development Status :: 3 - Alpha',

        # My Intended audience is mostly those who understand finance.
        'Intended Audience :: Financial and Insurance Industry',

        # My License is MIT.
        'License :: OSI Approved :: MIT License',

        # I wrote the client in English
        'Natural Language :: English',

        # The client should work on all OS.
        'Operating System :: OS Independent',

        # The client is intendend for PYTHON 3
        'Programming Language :: Python :: 3'
    ],

    # you will need python 3.7 to use this libary.
    python_requires='>=3.7'

)
