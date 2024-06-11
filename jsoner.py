import json


def dict_to_json(mydict: dict, json_file: str):
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(mydict, file, ensure_ascii=False, indent=4)


def json_to_var(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as file:
        myvar = json.load(file)
    return myvar