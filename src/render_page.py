import json
from wbib.queries import format_with_prefix, render_url

with open("src/books.json") as f:

    books = json.loads(f.read())


book_ol_ids = []
for shelf in books["shelves"]:

    for book in shelf["books"]:
        if "OL" in book:
            book_ol_ids.append(book)


# Implement logic to get author OL ids from API request

# Implement query to build map from OL ids

# Implement logging system for when OL ids are not on Wikidata

query_authors_map = f"""
#defaultView:Map
SELECT * WHERE {{

    VALUES ?book {values}
    ?book wdt:P50 ?author . 
    ?author wdt:P19 ?birthplace . 
    ?birthplace wdt:P625 ?geo .

    ?birthplace rdfs:label ?birthplaceLabel . 
    FILTER(LANG(?birthplaceLabel)="en")

    ?author rdfs:label ?authorLabel . 
    FILTER(LANG(?authorLabel)="en")
}}
"""

query_authors_map_url = render_url(query_authors_map)


site_title = "Tiago's books"

index = f"""



<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{site_title}</title>
    <meta property="og:description" content="powered by Wikidata" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous" />
    <link href="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js" rel="stylesheet"
        integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />
</head>

<body>

        <br />
                <h5 class="title is-5">Author map</h5>
        <p>
        <iframe width="75%" height="400" src="{query_authors_map_url}"></iframe>
        </p>
        <br />
</body>



"""

with open("index.html", "w+") as f:
    f.write(index)
