#!usr/bin/env python3

import requests
from datetime import datetime
import isbnlib
import sys
from dictionaries.dictionaries import dicts
from helper import add_key

if len(sys.argv) == 2:
    isbn = sys.argv[1]
else:
    isbn = input("ISBN:")


url = f"https://openlibrary.org/isbn/{isbn}.json"

r = requests.get(url)

data = r.json()
print(url)


title = data["title"]

isbn_13 = isbnlib.mask(data["isbn_13"][0])
open_library_id = data["key"].split("/")[-1]

try:
    date = datetime.strptime(data["publish_date"], "%b %d, %Y")
    publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/11")
except ValueError:
    try:
        date = datetime.strptime(data["publish_date"], "%Y")
        publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
    except ValueError:
        date = datetime.strptime(data["publish_date"], "%B %d, %Y")
        publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")


authors = []
for author in data["authors_open_library"]:
    author_id = author["key"].split("/")[-1]
    authors.append(dicts["authors"][author_id])

publishers = []
for publisher in data["publishers"]:
    publishers.append(dicts["publishers"][publisher])


lang = input("Language code:")
print(
    f"""
CREATE
LAST|Len|"{title}"
LAST|Den|"book edition"
LAST|Lpt|"{title}"
LAST|Dpt|"edição de livro"
LAST|P31|Q3331189
LAST|P1476|{lang}:"{title}"
LAST|P407|{dicts["langcode"][lang]}
LAST|P577|{publish_date}
LAST|P212|"{isbn_13}"
LAST|P648|"{open_library_id}"
"""
)

try:
    isbn_10 = isbnlib.mask(data["isbn_10"][0])

    print(f"""LAST|P957|"{isbn_10}" """)
except:
    pass
for author in authors:
    print(f"""LAST|P50|{author}""")

for publisher in publishers:
    print(f"""LAST|P123|{publisher}""")
