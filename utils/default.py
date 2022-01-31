import json
from collections import namedtuple

"""Thank you to AGB by Motzumoto for the Utils file"""
def config(filename: str = "config"):
    try:
        with open(f"{filename}.json", encoding="utf-8") as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("config.json file wasn't found")

def get(file):
    try:
        with open(file, encoding="utf-8") as data:
            return json.load(
                data, object_hook=lambda d: namedtuple("X", d.keys())(*d.values())
            )
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")