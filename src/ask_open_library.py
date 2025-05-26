#!/usr/bin/env python3

import sys
import requests
from pathlib import Path
import json

# ---- local utilities / data -------------------------------------------------
from dictionaries.dictionaries import dicts  # your look-up tables
from wdcuration import add_key  # semi-auto reconciliation

# --------------------------------------------------------------------------- #
HERE = Path(__file__).parent.resolve()
DICTS = HERE / "dictionaries"  # path to dictionaries


def get_json(url: str) -> dict:
    """Fetch JSON and fail verbosely."""
    print(f"# Fetching → {url}")
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        sys.exit(f"Error: {url} returned {r.status_code}")
    return r.json()


def main() -> None:
    # --- 0. Capture / normalize ISBN ---------------------------------------
    isbn = sys.argv[1] if len(sys.argv) > 1 else input("ISBN: ").strip()
    isbn = isbn.replace("-", "")
    print(f"# Looking up ISBN {isbn}")

    # --- 1. Edition JSON ----------------------------------------------------
    edition_url = f"https://openlibrary.org/isbn/{isbn}.json"
    edition = get_json(edition_url)

    # --- 2. Locate work key -------------------------------------------------
    works = edition.get("works", [])
    if not works:
        sys.exit(f"# No associated work found.\n# Edition JSON: {edition_url}")
    work_key = works[0]["key"]  # e.g. “/works/OL25788572W”
    work_url = f"https://openlibrary.org{work_key}.json"
    work_json = get_json(work_url)

    # --- 3. Basic work metadata --------------------------------------------
    title = work_json.get("title", "").strip()
    subtitle = work_json.get("subtitle", "")
    title_full = f"{title}: {subtitle}" if subtitle else title
    print(f"# Title → {title_full}")

    # --- 4. Authors ---------------------------------------------------------
    author_qids = []  # resolved to Wikidata items
    author_name_strings = []  # fallback (P2093)

    for a in work_json.get("authors", []):
        author_id = a.get("author", {}).get("key", "").split("/")[-1]  # OL2225618A
        local_map = dicts.get("authors_open_library", {})

        if author_id in local_map:
            qid = local_map[author_id]
            author_qids.append(qid)
            print(f"# Author {author_id} resolved locally → {qid}")
            continue

        # ---- 4a. fetch author JSON for name --------------------------------
        author_url = f"https://openlibrary.org/authors/{author_id}.json"
        author_json = get_json(author_url)
        author_name = author_json.get("name")
        authors_dict = dicts.get("authors_open_library", {})

        # ---- 4b. try wdcuration.add_key ------------------------------------
        qid = None
        if author_name:
            try:
                authors_dict = add_key(
                    authors_dict, author_id, search_string=author_name
                )

                author_dict_path = DICTS / "authors_open_library.json"
                with open(author_dict_path, "r+", encoding="utf-8") as f:
                    json.dump(authors_dict, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"# wdcuration.add_key error for {author_id}: {e}")

        # ---- 4c. route by result -------------------------------------------
        if isinstance(qid, str) and qid.startswith("Q"):
            author_qids.append(qid)
            # (add_key already patched dictionaries file on disk)
        else:
            # fallback: name string + OL author ID
            author_name_strings.append((author_name, author_id))
            print(f"# Fallback: {author_name} will be added via P2093 + P648")

    # --- 5. Language --------------------------------------------------------
    lang_code = "en"
    if work_json.get("languages"):
        lang_code = work_json["languages"][0]["key"].split("/")[-1]

    lang_qid = dicts.get("langcode", {}).get(lang_code)
    if not lang_qid:
        try:
            lang_qid = add_key("langcode", lang_code, search_string=lang_code)
            print(f"# add_key(lang) returned → {lang_qid}")
        except Exception as e:
            print(f"# wdcuration.add_key error for language {lang_code}: {e}")

    if not (isinstance(lang_qid, str) and lang_qid.startswith("Q")):
        print(f"# WARNING: unknown language {lang_code} – no P407 set.")
        lang_qid = None

    # --- 6. OpenLibrary Work ID --------------------------------------------
    ol_work_id = work_key.split("/")[-1]  # e.g. OL25788572W
    print(f"# OpenLibrary Work ID → {ol_work_id}")

    # --- 7. QuickStatements -------------------------------------------------
    print("\n# === QuickStatements ===")
    print("CREATE")
    print(f'LAST|Len|"{title_full}"')
    print('LAST|Den|"written work"')
    print("LAST|P31|Q47461344")
    print(f'LAST|P1476|{lang_code}:"{title_full}"')

    # authors with QIDs
    for q in author_qids:
        print(f"LAST|P50|{q}")

    # fallback name-string authors
    for name, aid in author_name_strings:
        print(f'LAST|P2093|"{name}"|P648|"{aid}"')

    # language statement
    if lang_qid:
        print(f"LAST|P407|{lang_qid}")

    # always attach the work’s own OpenLibrary ID
    print(f'LAST|P648|"{ol_work_id}"')

    print("# === End QuickStatements ===\n")
    print("# Inspect source JSONs:")
    print(f"# • Edition → {edition_url}")
    print(f"# • Work    → {work_url}")


if __name__ == "__main__":
    main()
