import json

with open("./configs/config.json","rt") as r:
    config = json.load(r)
    print(type(config["812606386592284672"]))