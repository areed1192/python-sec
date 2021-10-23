from bs4 import BeautifulSoup

import csv
import pprint
import pathlib
import collections
import xml.etree.ElementTree as ET
from typing import Union


class XbrlFiling():

    def __init__(self) -> None:

        self.file_path = None
        self.url = None

    def from_url(self, url: str) -> None:
        pass

    def from_file(self, file_path: Union[str, pathlib.Path]) -> None:
        pass
