# From https://mlhive.com/2022/02/read-and-write-pascal-voc-xml-annotations-in-python

import xml.etree.ElementTree as ET
import cv2
import numpy as np
from wbib.queries import format_with_prefix, render_url
from wikidata2df import wikidata2df
import json

with open("src/books.json") as f:

    books = json.loads(f.read())

book_qids = []
for shelf in books["shelves"]:
    if shelf["id"] == "thomaz":
        book_qids.extend(shelf["books"])


values = format_with_prefix(book_qids)

query_authors = f"""
SELECT * WHERE {{
    VALUES ?book {values}
    ?book wdt:P50 ?author . 
    ?author wdt:P27 ?nationality .
    
    ?nationality rdfs:label ?nationalityLabel . 
    FILTER(LANG(?nationalityLabel)="en")

    ?author rdfs:label ?authorLabel . 
    FILTER(LANG(?authorLabel)="en")
}}
"""

df = wikidata2df(query_authors)

print(df[["nationality", "nationalityLabel"]].drop_duplicates())

nation_qid = input("Enter the qid of the nation of interest:")

nationality = list(df["book"][df["nationality"] == nation_qid])

print(nationality)
# parse xml file
tree = ET.parse("data/thomaz.xml")
image = cv2.imread("data/thomaz.jpeg")
root = tree.getroot()  # get root object
height = int(root.find("size")[0].text)
width = int(root.find("size")[1].text)
channels = int(root.find("size")[2].text)

# https://pyimagesearch.com/2016/03/07/transparent-overlays-with-opencv/
overlay = image.copy()
output = image.copy()

bbox_coordinates = []
for member in root.findall("object"):
    class_name = member[0].text  # class name
    print(class_name)
    if class_name not in nationality:
        continue
    # bbox coordinates
    xmin = int(member[4][0].text)
    ymin = int(member[4][1].text)
    xmax = int(member[4][2].text)
    ymax = int(member[4][3].text)
    # store data in list
    bbox_coordinates.append([class_name, xmin, ymin, xmax, ymax])

    box_color = (255, 0, 0)
    cv2.rectangle(overlay, (xmin, ymin), (xmax, ymax), box_color, cv2.FILLED)


out = image.copy()
alpha = 0.7
cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

print("alpha={}, beta={}".format(alpha, 1 - alpha))
cv2.imshow("Output", output)
cv2.waitKey(0)

print(bbox_coordinates)
