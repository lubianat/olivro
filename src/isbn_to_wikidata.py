#!usr/bin/env python3

import requests
from datetime import datetime
import isbnlib

isbn = input("ISBN:")

url = f"https://openlibrary.org/isbn/{isbn}.json"

r = requests.get(url)

data = r.json()
print(url)


authors_dict = {
    "OL217344A": "Q258662",
    "OL347356A": "Q95202439",
    "OL7522004A": "Q465907",
}
publishers_dict = {"Companhia das Letras": "Q2990311", "Koenemann": "Q10552136"}
langcode_dict = {"pt": "Q5146", "en": "Q1860"}

title = data["title"]
isbn_10 = isbnlib.mask(data["isbn_10"][0])

isbn_13 = isbnlib.mask(data["isbn_13"][0])
open_library_id = data["key"].split("/")[-1]

try:
    date = datetime.strptime(data["publish_date"], "%b %d, %Y")
    publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/11")
except ValueError:
    date = datetime.strptime(data["publish_date"], "%Y")
    publish_date = datetime.strftime(date, "+%Y-%m-%dT00:00:00Z/09")

authors = []
for author in data["authors"]:
    author_id = author["key"].split("/")[-1]
    authors.append(authors_dict[author_id])

publishers = []
for publisher in data["publishers"]:
    publishers.append(publishers_dict[publisher])


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
LAST|P407|{langcode_dict[lang]}
LAST|P577|{publish_date}
LAST|P957|"{isbn_10}"
LAST|P212|"{isbn_13}"
LAST|P648|"{open_library_id}"
"""
)

for author in authors:
    print(f"""LAST|P50|{author}""")

for publisher in publishers:
    print(f"""LAST|P123|{publisher}""")
