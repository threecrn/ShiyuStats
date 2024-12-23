import json
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--all", action="store_true")
parser.add_argument("-d", "--duos", action="store_true")
parser.add_argument("-t", "--top", action="store_true")
parser.add_argument("-w", "--whale", action="store_true")

args = parser.parse_args()

with open(str(os.getenv("REPO_PATH")) + "/data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

with open(str(os.getenv("REPO_PATH")) + "/data/w-engine.json") as char_file:
    LIGHT_CONES = json.load(char_file)

# no need to add 2.2.1"_da"
RECENT_PHASE = "1.3.3"

# if no past phase, put invalid folder
# add 2.2.1"_da"
past_phase = "1.3.2"
global da_mode
global as_mode
# if as: da_mode = True
da_mode = True
as_mode = False
char_infographics = ["Zhu Yuan", "Ben", "Nicole"]
char_infographics = char_infographics[0]

# threshold for comps in character infographics, non-inclusive
global char_app_rate_threshold
char_app_rate_threshold = 0.25

# threshold for comps, not inclusive
global app_rate_threshold
global app_rate_threshold_round
global f2p_app_rate_threshold
app_rate_threshold = 0.1
app_rate_threshold_round = 0
json_threshold = 0
f2p_app_rate_threshold = 0.1
skew_num = 0.8
duo_dict_len = 30
duo_dict_len_print = 10

skip_self = False
skip_random = False
archetype = "all"
whaleOnly = args.whale
whaleSigWeap = False

# Char infographics should be separated from overall comp rankings
run_commands = [
    # "Duos check",
    "Char usages 8 - 10",
    "Char usages for each stage",
    "Char usages for each stage (combined)",
    # "Comp usage 8 - 10",
    # "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]

if args.whale or args.top:
    run_commands = [
        "Char usages 8 - 10",
        "Comp usage 8 - 10",
    ]

elif args.all:
    run_commands = [
        "Char usages 8 - 10",
        "Char usages for each stage",
        "Char usages for each stage (combined)",
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    ]

elif args.duos:
    run_commands = [
        "Duos check",
    ]

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold
