import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

with open('../data/w-engine.json') as char_file:
    LIGHT_CONES = json.load(char_file)

# no need to add 2.2.1"_pf"
RECENT_PHASE = "1.0.2"

# if no past phase, put invalid folder
# add 2.2.1"_pf"
past_phase = "1.0.1"
global pf_mode
global as_mode
# if as: pf_mode = True
pf_mode = False
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
whaleOnly = False
whaleSigWeap = False

# Char infographics should be separated from overall comp rankings
run_commands = [
    # "Duos check",
    "Char usages 8 - 10",
    "Char usages for each stage",
    "Char usages for each stage (combined)",
    "Comp usage 8 - 10",
    "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold