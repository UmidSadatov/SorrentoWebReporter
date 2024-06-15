import json


def var_to_json(myvar: dict | list, json_file: str):
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(myvar, file, ensure_ascii=False, indent=4)


def json_to_var(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as file:
        myvar = json.load(file)
    return myvar