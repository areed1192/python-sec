# Python SEC

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [Support These Projects](#support-these-projects)

## Overview

The Securities & Exchange Commission (SEC) has a treasure trove of business data available to indviduals for free. However, the biggest obstacle to getting this free data boils down to two challenges:

1. Figuring out where it is
2. Figuring out how to extract it

The Python SEC library (`pysec`) is designed to make the collection and the extraction of SEC data quick and effortless. The library was designed around some of the following goals:

1. Making the usage of the EDGAR search system, in a prgorammatic fashion, more intuitive.
2. Making the definition of queries more customizeable while still maintaining the overall clearity of the library.
3. Standardize the returning content so that content is organized consistently and ensuring gaps in data are filled in or extended that way navigating to other directories or files can be done dynamically.
4. Simplify the parsing of XBRL files so that data can be more easily manipulated.

## Setup

Right now, the library is not hosted on **PyPi** so you will need to do a local install on your system if you plan to use it in other scrips you use.

First, clone this repo to your local system. After you clone the repo, make sure to run the `setup.py` file, so you can install any dependencies you may need. To run the `setup.py` file, run the following command in your terminal.

```console
pip install python-sec
```

This will install all the dependencies listed in the `setup.py` file. Once done you can use the library wherever you want.

## Usage

Here is a simple example of using the `pysec` library to grab the index files for specific quarter.

```python
import pprint
from pysec.edgar import EDGARQuery

# Initialize the client.
edgar_client = EDGARQuery()

# Grab a specific Quarterly Archive Indexes.
quarterly_archives = edgar_client.get_quarterly_index(year=2000, quarter=4)
pprint.pprint(quarterly_archives)
```

You will note the output of the above code would look like the following:

```json
[
  {
    "href": "company.gz",
    "last_modified": "09/06/2014 01:08:55 AM",
    "name": "company.gz",
    "size": "1287 KB",
    "type": "file",
    "url": "https://www.sec.gov/Archives/edgar/full-index/2000/QTR4/company.gz"
  },
  ...{
    "href": "company.idx",
    "last_modified": "09/06/2014 01:08:53 AM",
    "name": "company.idx",
    "size": "10625 KB",
    "type": "file",
    "url": "https://www.sec.gov/Archives/edgar/full-index/2000/QTR4/company.idx"
  }
]
```

## Support these Projects

**Patreon:**
Help support this project and future projects by donating to my [Patreon Page](https://www.patreon.com/sigmacoding). I"m always looking to add more content for individuals like yourself, unfortuantely some of the APIs I would require me to pay monthly fees.

**YouTube:**
If you"d like to watch more of my content, feel free to visit my YouTube channel [Sigma Coding](https://www.youtube.com/c/SigmaCoding).

**Hire Me:**
If you have a project, you think I can help you with feel free to reach out at coding.sigma@gmail.com
