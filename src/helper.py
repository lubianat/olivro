import json
from dictionaries.dictionaries import dicts


def add_key(dictionary, string):
    qid = input(f"What is the qid for: {string} ?")

    dictionary[string] = qid
    return dictionary


def update_query_values(dict_key, key_now):
    dict_now = dicts[dict_key]
    print(dict_now)
    try:
        result = dict_now[key_now]
    except:
        dict_now = add_key(dict_now, key_now)

        with open(f"src/dictionaries/{dict_key}.json", "w+") as f:
            f.write(json.dumps(dict_now, indent=4))

    return result
