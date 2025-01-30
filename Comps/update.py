import json
import requests
import re
import io

download = requests.get("https://api.hakush.in/zzz/data/equipment.json").content.decode(
    "utf-8"
)
artifacts = json.load(io.StringIO(download))

with open("../data/drive_affixes.json") as artifact_file:
    artifacts2 = json.load(artifact_file)
# artifacts2 = {}

artifacts_affixes = {}
for artifact in artifacts:
    artifacts[artifact]["id"] = artifact
    artifacts[artifact]["name"] = artifacts[artifact]["EN"]["name"]
    artifacts[artifact]["desc"] = [
        artifacts[artifact]["EN"]["desc2"],
        artifacts[artifact]["EN"]["desc4"],
    ]
    del artifacts[artifact]["EN"]
    del artifacts[artifact]["KO"]
    del artifacts[artifact]["CHS"]
    del artifacts[artifact]["JA"]
    artifacts[artifact]["desc"][0] = re.sub("<.*?>", "", artifacts[artifact]["desc"][0])
    artifacts[artifact]["desc"][1] = re.sub("<.*?>", "", artifacts[artifact]["desc"][1])
    affix = artifacts[artifact]["desc"][0]

    if affix[-1] == ".":
        affix = affix[:-1]
    for i in ["DMG "]:
        affix = affix.replace(i, "")

    affix = affix.replace("increases by ", "+")
    if "Increases " in affix:
        affix = affix.replace("Increases ", "")
        affix = affix.replace("by ", "+")
    if "Reduces " in affix:
        affix = affix.replace("Reduces ", "")
        affix = affix.replace("by ", "-")
        # split = affix.split(" ")
        # affix = split[1] + " +" + split[0]

    affix = affix.replace("CRIT Rate", "CR")
    affix = affix.replace("Anomaly Proficiency", "AP")

    if affix not in artifacts_affixes:
        artifacts_affixes[affix] = []
    artifacts_affixes[affix].append(artifacts[artifact]["name"])

for artifact in list(artifacts_affixes.keys()):
    if len(artifacts_affixes[artifact]) > 1:
        if artifact not in artifacts2:
            if len(artifact) > 12:
                print("Set name too long: " + artifact)
            else:
                add_arti = input("Add " + artifact + "? (y/n): ")
        else:
            add_arti = "y"
        if add_arti == "y":
            artifacts2[artifact] = artifacts_affixes[artifact]
    else:
        del artifacts_affixes[artifact]
print()

with open("../data/drive_sets.json", "w") as out_file:
    out_file.write(json.dumps(artifacts, indent=4))

with open("../data/drive_affixes.json", "w") as out_file:
    out_file.write(json.dumps(artifacts2, indent=4))

with open("../data/w-engine.json") as char_file:
    wengine1 = json.load(char_file)
download = requests.get("https://api.hakush.in/zzz/data/weapon.json").content.decode(
    "utf-8"
)
wengine2 = json.load((io.StringIO(download)))

for weap in wengine2:
    weap_name = wengine2[weap]["EN"]
    if weap_name not in wengine1:
        # add_weap = input("Add " + weap_name + "? (y/n): ")
        # if add_weap == "y":
        wengine1[weap_name] = wengine2[weap].copy()
        wengine1[weap_name]["id"] = weap
        wengine1[weap_name]["name"] = weap_name

        if wengine2[weap]["rank"] == 2:
            wengine1[weap_name]["availability"] = "B"
        elif wengine2[weap]["rank"] == 3:
            wengine1[weap_name]["availability"] = "A"
        elif wengine2[weap]["rank"] == 4:
            # print(weap_name)
            # add_weap = input("Limited W-Engine? (y/n): ")
            # if add_weap == "y":
            wengine1[weap_name]["availability"] = "Limited S"
            # else:
            #     wengine1[weap_name]["availability"] = "Standard S"

        match str(wengine1[weap_name]["type"]):
            case "1":
                wengine1[weap_name]["role"] = "Damage Dealer"
            case "2":
                wengine1[weap_name]["role"] = "Stun"
            case "3":
                wengine1[weap_name]["role"] = "Damage Dealer"
            case "4":
                wengine1[weap_name]["role"] = "Support"
            case "5":
                wengine1[weap_name]["role"] = "Stun"

        del wengine1[weap_name]["rank"]
        del wengine1[weap_name]["type"]
        del wengine1[weap_name]["EN"]
        del wengine1[weap_name]["KO"]
        del wengine1[weap_name]["CHS"]
        del wengine1[weap_name]["JA"]

with open("../data/w-engine.json", "w") as out_file:
    out_file.write(json.dumps(wengine1, indent=4))


with open("../data/characters.json") as char_file:
    chars1 = json.load(char_file)
download = requests.get("https://api.hakush.in/zzz/data/character.json").content.decode(
    "utf-8"
)
chars2 = json.load((io.StringIO(download)))

for char in chars2:
    char_name = chars2[char]["EN"]
    if char_name not in chars1 and chars2[char]["icon"] != "":
        add_char = input("Add " + char_name + "? (y/n): ")
        if add_char == "y":
            chars1[char_name] = chars2[char].copy()
            chars1[char_name]["id"] = char
            chars1[char_name]["name"] = char_name

            if chars2[char]["rank"] == 3:
                chars1[char_name]["availability"] = "A"
            elif chars2[char]["rank"] == 4:
                print(char_name)
                add_char = input("Limited Character? (y/n): ")
                if add_char == "y":
                    chars1[char_name]["availability"] = "Limited S"
                else:
                    chars1[char_name]["availability"] = "Standard S"

            # print("Role? 0: DPS, 1: Amplifier, 2: Sustain")
            # role_char = input()
            # match str(role_char):
            match str(chars1[char_name]["type"]):
                case "1":
                    chars1[char_name]["role"] = "Damage Dealer"
                case "2":
                    chars1[char_name]["role"] = "Stun"
                case "3":
                    chars1[char_name]["role"] = "Damage Dealer"
                case "4":
                    chars1[char_name]["role"] = "Support"
                case "5":
                    chars1[char_name]["role"] = "Support"

            match str(chars1[char_name]["element"]):
                case "200":
                    chars1[char_name]["element"] = "Physical"
                case "201":
                    chars1[char_name]["element"] = "Fire"
                case "202":
                    chars1[char_name]["element"] = "Ice"
                case "203":
                    chars1[char_name]["element"] = "Electric"
                case "205":
                    chars1[char_name]["element"] = "Ether"

            match str(chars1[char_name]["camp"]):
                case "1":
                    chars1[char_name]["camp"] = "Cunning Hares"
                case "2":
                    chars1[char_name]["camp"] = "Victoria Housekeeping Co."
                case "3":
                    chars1[char_name]["camp"] = "Belobog Heavy Industries"
                case "4":
                    chars1[char_name]["camp"] = "Sons of Calydon"
                case "5":
                    chars1[char_name]["camp"] = "Obol Squad"
                case "6":
                    chars1[char_name]["camp"] = "Hollow Special Operations Section 6"
                case "7":
                    chars1[char_name]["camp"] = "New Eridu Public Security"
                case "8":
                    chars1[char_name]["camp"] = "Stars of Lyra"
                case _:
                    print("Unavailable camp: " + str(chars1[char_name]["camp"]))

            del chars1[char_name]["code"]
            del chars1[char_name]["rank"]
            del chars1[char_name]["type"]
            del chars1[char_name]["hit"]
            del chars1[char_name]["EN"]
            del chars1[char_name]["KO"]
            del chars1[char_name]["CHS"]
            del chars1[char_name]["JA"]

with open("../data/characters.json", "w") as out_file:
    out_file.write(json.dumps(chars1, indent=4))


with open("../data/bangboos.json") as bangboo_file:
    bangboos1 = json.load(bangboo_file)
download = requests.get("https://api.hakush.in/zzz/data/bangboo.json").content.decode(
    "utf-8"
)
bangboos2 = json.load((io.StringIO(download)))

for bangboo in bangboos2:
    bangboo_name = bangboos2[bangboo]["EN"]
    if bangboo_name not in bangboos1 and bangboos2[bangboo]["icon"] != "":
        add_bangboo = input("Add " + bangboo_name + "? (y/n): ")
        if add_bangboo == "y":
            bangboos1[bangboo_name] = bangboos2[bangboo].copy()
            bangboos1[bangboo_name]["id"] = bangboo
            bangboos1[bangboo_name]["name"] = bangboo_name

            if bangboos2[bangboo]["rank"] == 3:
                bangboos1[bangboo_name]["availability"] = "A"
            elif bangboos2[bangboo]["rank"] == 4:
                bangboos1[bangboo_name]["availability"] = "S"

            # print("Role? 0: DPS, 1: Amplifier, 2: Sustain")
            # role_bangboo = input()
            # match str(role_bangboo):

            del bangboos1[bangboo_name]["codename"]
            del bangboos1[bangboo_name]["rank"]
            del bangboos1[bangboo_name]["EN"]
            del bangboos1[bangboo_name]["KO"]
            del bangboos1[bangboo_name]["CHS"]
            del bangboos1[bangboo_name]["JA"]

with open("../data/bangboos.json", "w") as out_file:
    out_file.write(json.dumps(bangboos1, indent=4))

# download = requests.get("https://github.com/Mar-7th/StarRailRes/raw/master/index_new/en/simulated_blessings.json").content.decode('utf-8')
# with open("../data/simulated_blessings.json", "w") as out_file:
#     out_file.write(json.dumps(json.load(io.StringIO(download)),indent=4))

# download = requests.get("https://github.com/Mar-7th/StarRailRes/raw/master/index_new/en/simulated_curios.json").content.decode('utf-8')
# curio_json = json.load(io.StringIO(download))
# curio_json["901"] = curio_json["109"].copy()
# curio_json["902"] = curio_json["109"].copy()
# curio_json["901"]["id"] = "901"
# curio_json["902"]["id"] = "902"
# with open("../data/simulated_curios.json", "w") as out_file:
#     out_file.write(json.dumps(curio_json,indent=4))

# download = requests.get("https://github.com/Mar-7th/StarRailRes/raw/master/index_new/en/simulated_blocks.json").content.decode('utf-8')
# with open("../data/simulated_blocks.json", "w") as out_file:
#     out_file.write(json.dumps(json.load(io.StringIO(download)),indent=4))
