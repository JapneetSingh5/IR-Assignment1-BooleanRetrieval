from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import sys
import re
import os
import json
import string

coll_path = sys.argv[0]
indexfile = sys.argv[1]
stopwordfile = sys.argv[2]
compression = int(sys.argv[3])
xml_tags_info = sys.argv[4]

