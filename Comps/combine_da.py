import json
from copy import deepcopy
from slugify import slugify

temp_stats = []
with open("../Comps/prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)
with open("../char_results/all.json") as char_file:
    CHARACTERS = json.load(char_file)
with open("../char_results/appearance.json") as app_char_file:
    APP = json.load(app_char_file)
    DEFAULT_APP = deepcopy(APP)
with open("../char_results/rounds.json") as round_char_file:
    ROUND = json.load(round_char_file)
    DEFAULT_ROUND = deepcopy(ROUND)

for i in range(1, 4):
    for app_char_iter in DEFAULT_APP[f"1-{i}"]["4"]:
        new_key = slugify(app_char_iter)
        if new_key in slug:
            new_key = slug[new_key]
        APP[f"1-{i}"]["4"][new_key] = APP[f"1-{i}"]["4"].pop(app_char_iter)
    for round_char_iter in DEFAULT_ROUND[f"1-{i}"]["4"]:
        new_key = slugify(round_char_iter)
        if new_key in slug:
            new_key = slug[new_key]
        ROUND[f"1-{i}"]["4"][new_key] = ROUND[f"1-{i}"]["4"].pop(round_char_iter)

for iter_char in range(len(CHARACTERS)):
    app_dict = {}
    for i in range(1, 4):
        app_dict = app_dict | {
            f"1-{i}_app": APP[f"1-{i}"]["4"][CHARACTERS[iter_char]["char"]]["app"],
            f"1-{i}_round": ROUND[f"1-{i}"]["4"][CHARACTERS[iter_char]["char"]][
                "round"
            ],
        }
    temp_stats.append(CHARACTERS[iter_char] | app_dict)
    # temp_stats.append((CHARACTERS[iter_char]) | app_dict)

with open("../char_results/all2.json", "w") as char_file:
    char_file.write(json.dumps(temp_stats, indent=2))
