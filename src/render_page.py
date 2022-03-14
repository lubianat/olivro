import json
from wbib.queries import format_with_prefix, render_url

with open("src/books.json") as f:

    books = json.loads(f.read())


book_qids = []
for shelf in books["shelves"]:
    book_qids.extend(shelf["books"])


values = format_with_prefix(book_qids)

query_books = """
SELECT * WHERE {
    VALUES ?book {value}
    ?book rdfs:label ?bookLabel . 
    FILTER(LANG(?bookLabel)="en")
}
"""

query_books_url = render_url(query_books)


query_authors = """
SELECT * WHERE {
    VALUES ?book {value}
    ?book wdt:P50 ?author . 
    ?author rdfs:label ?authorLabel . 
    FILTER(LANG(?authorLabel)="en")
}
"""

query_authors_url = render_url(query_authors)


query_authors_map = """
#defaultType:Map
SELECT * WHERE {
    VALUES ?book {value}
    ?book wdt:P50 ?author . 
    ?author wdt:P19 ?birthplace . 
    ?birthplace wdt:P625 ?geo . 
    ?author rdfs:label ?authorLabel . 
    FILTER(LANG(?authorLabel)="en")
}
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

        <h5 class="title is-5">All books</h5>
        <p>
            <iframe width="75%" height="400" src="{query_books_url}"></iframe>
        </p>
        <br />
        <h5 class="title is-5">All books</h5>
        <p>
            <iframe width="75%" height="400" src="{query_authors_url}"></iframe>
        </p>
        <br />
                <h5 class="title is-5">All books</h5>
        <p>
        <iframe width="75%" height="400" src="{query_authors_map_url}"></iframe>
        </p>
        <br />
</body>



"""

with open("index.html", "w+") as f:
    f.write(index)
