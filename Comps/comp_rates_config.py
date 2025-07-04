import argparse
import json
import os

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-off", "--offline_collect", action="store_true")
parser.add_argument("-save", "--save_to_file", action="store_true")
parser.add_argument("-a", "--all", action="store_true")
parser.add_argument("-ca", "--comps_all", action="store_true")
parser.add_argument("-d", "--duos", action="store_true")
parser.add_argument("-t", "--top", action="store_true")
parser.add_argument("-cht", "--chars_top", action="store_true")
parser.add_argument("-ct", "--comps_top", action="store_true")
parser.add_argument("-w", "--whale", action="store_true")
parser.add_argument("-f", "--f2p", action="store_true")

parser.add_argument(
    "-sd",
    "--shiyu_defense",
    action="store_true",
)
parser.add_argument(
    "-da",
    "--deadly_assault",
    action="store_true",
)

args = parser.parse_args()

# For enka.network
offline_collect = args.offline_collect
save_to_file = args.save_to_file

with open(str(os.getenv("REPO_PATH")) + "/data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

with open(str(os.getenv("REPO_PATH")) + "/data/w-engine.json") as char_file:
    WENGINE = json.load(char_file)

# no need to add 2.2.1"_da"
RECENT_PHASE = "2.0.2"

# if no past phase, past_phase = "null"
past_phase = "2.0.1"
global da_mode
# if as: da_mode = True
da_mode = args.deadly_assault

if not da_mode:
    da_mode = False

suffix = ""
if da_mode:
    suffix = "_da"
RECENT_PHASE_PF = RECENT_PHASE + suffix
past_phase = past_phase + suffix

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
f2pOnly = args.f2p

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

if args.whale or args.top or args.f2p:
    run_commands = [
        "Char usages 8 - 10",
        "Comp usage 8 - 10",
    ]

elif args.chars_top:
    run_commands = [
        "Char usages 8 - 10",
    ]

elif args.comps_top:
    run_commands = [
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

elif args.comps_all:
    run_commands = [
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    ]

elif args.duos:
    run_commands = [
        "Duos check",
    ]

sigWeaps: list[str] = []
for wengine in WENGINE:
    if WENGINE[wengine]["availability"] == "Limited S":
        sigWeaps += [WENGINE[wengine]["name"]]

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold
