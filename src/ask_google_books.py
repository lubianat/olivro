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

data = isbnlib.meta(isbn)
print(data)


title = data["Title"]


query_values = {}


isbn_13 = isbnlib.mask(data["ISBN-13"])

date_original = data["Year"]
try:
    date = datetime.strptime(date_original, "%b %d, %Y")
    publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/11")
except ValueError:
    try:
        date = datetime.strptime(date_original, "%Y")
        publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
    except ValueError:
        try:
            date = datetime.strptime(date_original, "%B %d, %Y")
            publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
        except ValueError:
            try:
                date = datetime.strptime(date_original, "%Y-%m-%dT00:00:01Z")
                publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")
            except ValueError:
                date = datetime.strptime(date_original, "%YT")
                publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")


query_values["authors"] = []

for author in data["Authors"]:
    query_values["authors"].append(
        update_query_values(dict_key="authors", key_now=author)
    )

query_values["publishers"] = [
    update_query_values(dict_key="publishers", key_now=data["Publisher"])
]


lang = data["Language"]

if lang == "en_US":
    lang = "en"
if lang == "pt-BR":
    lang = "pt"
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
