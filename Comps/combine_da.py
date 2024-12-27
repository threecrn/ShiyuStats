import json

temp_stats = []
with open("../char_results/all.json") as char_file:
    CHARACTERS = json.load(char_file)
with open("../char_results/appearance.json") as app_char_file:
    APP = json.load(app_char_file)
with open("../char_results/rounds.json") as round_char_file:
    ROUND = json.load(round_char_file)
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
