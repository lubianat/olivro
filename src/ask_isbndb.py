#!usr/bin/env python3

import requests
from datetime import datetime
import isbnlib
import sys
from key import *
from dictionaries.dictionaries import dicts
from helper import *
import json

if len(sys.argv) == 2:
    isbn = sys.argv[1]
else:
    isbn = input("ISBN:")

url = f"https://api2.isbndb.com/book/{isbn}"

h = {"Authorization": isbndb_key}


r = requests.get(url, headers=h)
data = r.json()
data = data["book"]
print(data)
title = data["title"]


query_values = {}


isbn_13 = isbnlib.mask(data["isbn13"])
try:
    date = datetime.strptime(data["date_published"], "%b %d, %Y")
    publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/11")
except ValueError:
    try:
        date = datetime.strptime(data["date_published"], "%Y")
        publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
    except ValueError:
        try:
            date = datetime.strptime(data["date_published"], "%B %d, %Y")
            publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
        except ValueError:
            date = datetime.strptime(data["date_published"], "%Y-%m-%dT00:00:01Z")
            publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")

query_values["authors"] = []

for author in data["authors"]:
    query_values["authors"].append(
        update_query_values(dict_key="authors", key_now=author)
    )

query_values["publishers"] = [
    update_query_values(dict_key="publishers", key_now=data["publisher"])
]


lang = data["language"]

if lang == "en_US":
    lang = "en"

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
"""
)

try:
    isbn_10 = isbnlib.mask(data["isbn"])

    print(f"""LAST|P957|"{isbn_10}" """)
except:
    pass
for author in query_values["authors"]:
    print(f"""LAST|P50|{author}""")

for publisher in query_values["publishers"]:
    print(f"""LAST|P123|{publisher}""")
