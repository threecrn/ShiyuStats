"""Compile all ZZZ data."""

from __future__ import annotations

import csv
import os
import statistics
import time
from itertools import permutations
from sys import exit as sys_exit

import char_usage as cu
from comp_rates_config import (
    CHARACTERS,
    DEFAULT_ROUND,
    RECENT_PHASE,
    app_rate_threshold,
    app_rate_threshold_round,
    archetype,
    char_app_rate_threshold,
    char_infographics,
    da_mode,
    duo_dict_len,
    f2p_only,
    json,
    json_threshold,
    past_phase,
    run_commands,
    sig_weaps,
    skip_random,
    skip_self,
    whale_only,
)
from composition import Composition
from player_phase import PlayerPhase
from plyer import notification  # type: ignore[reportMissingTypeStubs]
from slugify import slugify

with open("prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)


for make_path in [
    "../comp_results",
    "../comp_results/json",
    "../enka.network",
    "../enka.network/results_real",
    "../char_results",
    "../rogue_results",
]:
    if not os.path.exists(make_path):
        os.makedirs(make_path)

start_time = time.time()
print("start")

if os.path.isfile("../../uids.csv"):
    with open("../../uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        self_uids = next(iter(reader))
else:
    self_uids = []

da_filename = "_da" if da_mode else ""
with (
    open("../data/raw_csvs_real/" + RECENT_PHASE + da_filename + ".csv")
    if os.path.exists("../data/raw_csvs_real/")
    else open("../data/raw_csvs/" + RECENT_PHASE + da_filename + ".csv")
) as f:
    stats = f
    reader = csv.reader(stats)
    next(reader)
    reader = list(reader)
all_comps: list[Composition] = []
all_chambers = ["1"] if da_mode else ["1", "2", "3", "4", "5", "6", "7"]
three_star_sample = {}
for chamber_num in all_chambers:
    three_star_sample[chamber_num] = 0

# uid_freq_comp will help detect duplicate UIDs
uid_freq_comp: dict[str, int] = {}
self_freq_comp: dict[str, int] = {}
last_uid = "0"
skip_uid = False

for line in reader:
    star_num = 0
    match str(line[3]):
        case "B":
            star_num = 1
        case "A":
            star_num = 2
        case "S":
            star_num = 3
        case _:
            if not (da_mode):
                print("Unknown star num")
    if skip_self and line[0] in self_uids:
        continue
    if skip_random and line[0] not in self_uids:
        continue
    if line[0] != last_uid:
        skip_uid = False
        if line[0] in uid_freq_comp:
            skip_uid = True
        elif (not da_mode and star_num > 0) or (
            da_mode and int("".join(filter(str.isdigit, line[2]))) > 0
        ):
            uid_freq_comp[line[0]] = 1
            if line[0] in self_uids:
                self_freq_comp[line[0]] = 1
        else:
            skip_uid = True
    last_uid = line[0]
    if not skip_uid:
        stage = str(line[1])
        comp_chars_temp: list[str] = []
        cons_chars_temp: list[int] = []
        for i in [6, 8, 10] if da_mode else [5, 7, 9]:
            if line[i] != "" and line[i] in CHARACTERS:
                comp_chars_temp.append(line[i])
                cons_chars_temp.append(int(float(line[i + 1])))
        if comp_chars_temp:
            comp = (
                Composition(
                    line[0],
                    comp_chars_temp,
                    RECENT_PHASE,
                    line[3],
                    int(line[2]),
                    "1-" + stage,
                    line[12],
                    cons_chars_temp,
                )
                if da_mode
                else Composition(
                    line[0],
                    comp_chars_temp,
                    RECENT_PHASE,
                    line[4],
                    star_num,
                    stage + "-" + str(line[2]),
                    line[11],
                    cons_chars_temp,
                )
            )
            all_comps.append(comp)
            if int(star_num) == 3:
                three_star_sample[stage] += 1

sample_size = {}
for chamber_num in all_chambers:
    sample_size[chamber_num] = {}
avg_round_stage: dict[str, list[int]] = {}
for chamber_num in all_chambers:
    avg_round_stage[chamber_num] = []
if os.path.exists("../char_results/duo_check.csv"):
    with open("../char_results/duo_check.csv") as f:
        valid_duo_dps = list(csv.reader(f, delimiter=","))
else:
    valid_duo_dps = []
sample_size["all"] = {
    "total": len(uid_freq_comp),
    "self_report": len(self_freq_comp),
    "random": len(uid_freq_comp) - len(self_freq_comp),
}
if da_mode:
    sample_size["1"] = sample_size["all"].copy()

with (
    open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
    if os.path.exists("../data/raw_csvs_real/")
    else open("../data/raw_csvs/" + RECENT_PHASE + "_char.csv")
) as f:
    stats = f
    reader = csv.reader(stats)
    next(reader)
    reader = list(reader)

all_players: dict[str, dict[str, PlayerPhase]] = {}
all_players[RECENT_PHASE] = {}
player = PlayerPhase(last_uid, RECENT_PHASE)
# uid_freq_char and last_uid will help detect duplicate UIDs
last_uid = "0"
uid_freq_char: list[str] = []

# Append lines
for line in reader:
    line[1] = RECENT_PHASE
    if line[0] in uid_freq_comp:
        if line[0] != last_uid:
            skip_uid = False
            if line[0] in uid_freq_char:
                skip_uid = True
            else:
                uid_freq_char.append(line[0])
        if not skip_uid:
            if line[0] != last_uid:
                all_players[RECENT_PHASE][last_uid] = player
                last_uid = line[0]
                player = PlayerPhase(last_uid, RECENT_PHASE)
            player.add_character(
                line[2],
                line[3],
                line[4],
                line[5],
                line[6],
                line[7],
            )
all_players[RECENT_PHASE][last_uid] = player

for comp in all_comps:
    if comp.player not in all_players[comp.phase]:
        all_players[comp.phase][comp.player] = PlayerPhase(comp.player, comp.phase)
    all_players[comp.phase][comp.player].add_comp(comp)

with open("../char_results/uids.csv", "w", newline="") as f:
    csv_writer = csv.writer(f)
    for uid in uid_freq_comp:
        csv_writer.writerow([uid])

cur_time = time.time()
print("done csv: ", (cur_time - start_time), "s")

all_comps_json = {}
all_comp_uids: set[str] = set()
if da_mode:
    three_stages = ["1-1", "1-2", "1-3"]
    three_double_stages = [["1-1", "1-2", "1-3"]]
    one_stage = ["1-1", "1-2", "1-3"]
    all_stages = ["1-1", "1-2", "1-3"]
else:
    one_stage = ["7-1", "7-2"]

    three_stages = [
        "1-1",
        "1-2",
        "2-1",
        "2-2",
        "3-1",
        "3-2",
        "4-1",
        "4-2",
        "5-1",
        "5-2",
        "6-1",
        "6-2",
        "7-1",
        "7-2",
    ]
    three_double_stages = [
        ["1-1", "1-2"],
        ["2-1", "2-2"],
        ["3-1", "3-2"],
        ["4-1", "4-2"],
        ["5-1", "5-2"],
        ["6-1", "6-2"],
        ["7-1", "7-2"],
    ]
    all_stages = [
        "1-1",
        "1-2",
        "2-1",
        "2-2",
        "3-1",
        "3-2",
        "4-1",
        "4-2",
        "5-1",
        "5-2",
        "6-1",
        "6-2",
        "7-1",
        "7-2",
    ]


def main() -> None:
    """Compile data."""
    global usage
    usage = {}
    global boo_usage
    boo_usage = {}

    if "Char usages all stages" in run_commands:
        char_usages(all_stages, filename="all")
        cur_time = time.time()
        print("done char: ", (cur_time - start_time), "s")

    if "Duos check" in run_commands:
        usage, boo_usage = char_usages(
            three_stages,
            filename="all",
        )
        duo_usages(
            all_comps,
            all_players,
            usage,
            archetype,
            three_stages,
        )

    if "Char usages 8 - 10" in run_commands:
        usage, boo_usage = char_usages(
            one_stage,
            filename="all",
        )
        if not whale_only and not f2p_only:
            duo_usages(
                all_comps,
                all_players,
                usage,
                archetype,
                one_stage,
            )
        cur_time = time.time()
        print("done char 8 - 10: ", (cur_time - start_time), "s")

    if "Char usages for each stage" in run_commands:
        char_chambers: dict[str, dict[int, dict[str, cu.CharUsageData]]] = {
            "all": {},
        }
        boo_chambers: dict[str, dict[int, dict[str, cu.CharUsageData]]] = {
            "all": {},
        }
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
            boo_chambers["all"][star_num] = boo_usage[star_num].copy()
        # for room in all_stages:
        for room in three_stages:
            char_chambers[room], boo_chambers[room] = char_usages(
                [room],
                filename=room,
            )

        appearances_write, rounds_write = compile_app_round(char_chambers)
        if not whale_only and not f2p_only:
            with open("../char_results/appearance.json", "w") as out_file:
                out_file.write(json.dumps(appearances_write, indent=2))
            with open("../char_results/rounds.json", "w") as out_file:
                out_file.write(json.dumps(rounds_write, indent=2))

        appearances_write, rounds_write = compile_app_round(boo_chambers)
        if not whale_only and not f2p_only:
            with open("../char_results/bangboo_appearance.json", "w") as out_file:
                out_file.write(json.dumps(appearances_write, indent=2))
            with open("../char_results/bangboo_rounds.json", "w") as out_file:
                out_file.write(json.dumps(rounds_write, indent=2))

        cur_time = time.time()
        print("done char stage: ", (cur_time - start_time), "s")

    if "Char usages for each stage (combined)" in run_commands:
        char_chambers = {"all": {}}
        boo_chambers = {"all": {}}
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
            boo_chambers["all"][star_num] = boo_usage[star_num].copy()
        # for room in all_double_stages:
        for room in three_double_stages:
            char_chambers[room[0]], boo_chambers[room[0]] = char_usages(
                room,
                filename=room[0].split("-")[0],
            )

        appearances_write, rounds_write = compile_app_round(char_chambers)
        if not whale_only and not f2p_only:
            with open("../char_results/appearance_combine.json", "w") as out_file:
                out_file.write(json.dumps(appearances_write, indent=2))
            with open("../char_results/rounds_combine.json", "w") as out_file:
                out_file.write(json.dumps(rounds_write, indent=2))

        appearances_write, rounds_write = compile_app_round(boo_chambers)
        if not whale_only and not f2p_only:
            with open(
                "../char_results/bangboo_appearance_combine.json",
                "w",
            ) as out_file:
                out_file.write(json.dumps(appearances_write, indent=2))
            with open("../char_results/bangboo_rounds_combine.json", "w") as out_file:
                out_file.write(json.dumps(rounds_write, indent=2))

        cur_time = time.time()
        print("done char stage (combine): ", (cur_time - start_time), "s")

    if "Comp usage all stages" in run_commands:
        comp_usages(all_stages, filename="all", floor=True)
        cur_time = time.time()
        print("done comp all: ", (cur_time - start_time), "s")

    if "Comp usage 8 - 10" in run_commands:
        comp_usages(one_stage, filename="top", floor=True)
        cur_time = time.time()
        print("done comp 8 - 10: ", (cur_time - start_time), "s")

    if "Comp usages for each stage" in run_commands:
        # for room in all_stages:
        for room in three_stages:
            comp_usages(
                [room],
                filename=room,
            )

        if not whale_only and not f2p_only:
            with open("../char_results/demographic.json", "w") as out_file:
                out_file.write(json.dumps(sample_size, indent=2))
        cur_time = time.time()
        print("done comp stage: ", (cur_time - start_time), "s")

    if "Character specific infographics" in run_commands:
        comp_usages(
            one_stage,
            filename=char_infographics,
            info_char=True,
            floor=True,
        )
        cur_time = time.time()
        print("done char infographics: ", (cur_time - start_time), "s")

    if (
        "Comp usage 8 - 10" in run_commands
        and "Comp usages for each stage" in run_commands
        and not whale_only
        and not f2p_only
    ):
        with open("../comp_results/json/all_comps.json", "w") as out_file:
            out_file.write(json.dumps(all_comps_json, indent=2))

    if __name__ == "__main__" and notification.notify:
        notification.notify(
            title="Finished",
            message="Finished executing comp_rates",
            # displaying time
            timeout=2,
        )
        # waiting time
        time.sleep(2)


def compile_app_round(
    char_chambers: dict[str, dict[int, dict[str, cu.CharUsageData]]],
) -> tuple[
    dict[str, dict[int, dict[str, dict[str, float | str]]]],
    dict[str, dict[int, dict[str, dict[str, float | str]]]],
]:
    """Compile appearance and round data."""
    appearances: dict[str, dict[int, dict[str, cu.CharUsageData]]] = {}
    rounds: dict[str, dict[int, dict[str, cu.CharUsageData]]] = {}
    appearances_write: dict[
        str,
        dict[int, dict[str, dict[str, float | str]]],
    ] = {}
    rounds_write: dict[str, dict[int, dict[str, dict[str, float | str]]]] = {}
    for room, char_cham in char_chambers.items():
        appearances[room] = {}
        rounds[room] = {}
        appearances_write[room] = {}
        rounds_write[room] = {}
        for star_num in char_cham:
            appearances[room][star_num] = dict(
                sorted(
                    char_cham[star_num].items(),
                    key=lambda t: t[1].app,
                    reverse=True,
                ),
            )
            appearances_write[room][star_num] = {}
            rounds_write[room][star_num] = {}
            rounds[room][star_num] = dict(
                sorted(
                    char_cham[star_num].items(),
                    key=lambda t: t[1].round,
                    reverse=da_mode,
                ),
            )
            for char in char_cham[star_num]:
                appearances_write[room][star_num][char] = {
                    "app": char_cham[star_num][char].app,
                    "rarity": char_cham[star_num][char].rarity,
                    "diff": char_cham[star_num][char].diff,
                }
                if char_cham[star_num][char].round == 0:
                    continue
                rounds_write[room][star_num][char] = {
                    "round": char_cham[star_num][char].round,
                    "rarity": char_cham[star_num][char].rarity,
                    "diff": char_cham[star_num][char].diff_rounds,
                }
    return (appearances_write, rounds_write)


def comp_usages(
    rooms: list[str],
    filename: str = "comp_usages",
    info_char: bool = False,
    floor: bool = False,
) -> None:
    """Comp usage."""
    global top_comps_app
    top_comps_app = {}
    comps_dict = used_comps(all_players, all_comps, rooms, filename)
    rank_usages(comps_dict, rooms)
    comp_usages_write(comps_dict, filename, floor, info_char, True)
    comp_usages_write(comps_dict, filename, floor, info_char, False)


class CompUsage(Composition):
    """Comp usage class."""

    def __init__(self, comp: Composition) -> None:
        """Comp usage constructor."""
        self.__dict__.update(comp.__dict__)
        del self.player
        self.uses = 0
        self.owns = 0
        self.round_num = {str(i): list[int]() for i in range(1, 13)}
        self.whale_count = set[str]()
        self.players = set[str]()
        self.is_count_round: bool
        self.is_count_round_print: bool
        self.app_rate: float
        self.round: float
        self.usage_rate: float
        self.own_rate: float
        self.app_rank: int


def used_comps(
    players: dict[str, dict[str, PlayerPhase]],
    comps: list[Composition],
    rooms: list[str],
    filename: str,
    phase: str = RECENT_PHASE,
) -> list[dict[tuple[str, ...], CompUsage]]:
    """Return the dictionary of all the comps used and how many times they were used."""
    comps_dict: list[dict[tuple[str, ...], CompUsage]] = [{}, {}, {}, {}, {}]
    total_self_comps = 0
    all_comp_uids.clear()
    all_comp_self_uids: set[str] = set()
    whale_count = 0
    f2p_count = 0

    for comp in comps:
        comp_tuple = tuple(comp.characters)
        cur_room = next(iter(str(comp.room).split("-")))
        # Check if the comp is used in the rooms that are being checked
        if comp.room not in rooms:
            continue

        all_comp_uids.add(comp.player)
        if comp.player in self_uids:
            total_self_comps += 1
            all_comp_self_uids.add(comp.player)
        if len(comp_tuple) < 3:
            continue

        whale_comp = False
        f2p_comp = True
        dps_count = 0
        for char in range(3):
            if CHARACTERS[comp_tuple[char]]["availability"] == "Limited S":
                if comp.char_cons:
                    if comp.char_cons[comp_tuple[char]] > 0:
                        whale_comp = True
                elif (
                    comp_tuple[char] in players[phase][comp.player].owned
                    and players[phase][comp.player].owned[comp_tuple[char]].cons > 0
                ):
                    whale_comp = True
            if (
                comp_tuple[char] in players[phase][comp.player].owned
                and players[phase][comp.player].owned[comp_tuple[char]].weapon
                not in sig_weaps
            ):
                f2p_comp = False
            if CHARACTERS[comp_tuple[char]]["role"] == "Damage Dealer":
                dps_count += 1
            for duo_dps in valid_duo_dps:
                if set(duo_dps).issubset(comp_tuple):
                    dps_count = 1
                    break

        if whale_comp:
            whale_count += 1
        if whale_only and not whale_comp:
            continue
        if f2p_comp:
            f2p_count += 1
        if f2p_only and (not f2p_comp or whale_comp):
            continue
        if da_mode:
            if not whale_comp and comp.round_num > 50000:
                continue
        elif whale_comp:
            if comp.round_num < 10:
                continue
        elif comp.round_num < 20:
            continue

        if comp_tuple not in comps_dict[4]:
            comps_dict[4][comp_tuple] = CompUsage(comp)
        comps_dict[4][comp_tuple].uses += 1
        comps_dict[4][comp_tuple].players.add(comp.player)
        if whale_comp:
            comps_dict[4][comp_tuple].whale_count.add(comp.player)
        if whale_comp == whale_only and (not f2p_only or f2p_comp):
            comps_dict[4][comp_tuple].round_num[cur_room].append(comp.round_num)
            if dps_count == 1:
                avg_round_stage[cur_room].append(
                    comp.round_num,
                )

    for stage, round_stage in avg_round_stage.items():
        sample_size[stage]["avg_round"] = round(
            statistics.mean(round_stage if round_stage else [0]),
            2,
        )

    chamber_num = list(str(filename).split("-"))
    if len(chamber_num) > 1 and chamber_num[1] == "1" and not da_mode:
        sample_size[chamber_num[0]]["total"] = len(all_comp_uids)
        sample_size[chamber_num[0]]["self_report"] = len(all_comp_self_uids)
        sample_size[chamber_num[0]]["random"] = len(all_comp_uids) - len(
            all_comp_self_uids,
        )
    if whale_only:
        print("Whale percentage: " + str(whale_count / len(all_comp_uids)))
    return comps_dict


def rank_usages(
    comps_dict: list[dict[tuple[str, ...], CompUsage]],
    rooms: list[str],
) -> None:
    """Calculate the usage rate and sort the comps according to it."""
    # Calculate the usage rate and sort the comps according to it
    total = len(all_comp_uids) / 100.0
    rates: list[float] = []
    for comp in comps_dict[4]:
        avg_round: list[float] = []
        uses_room: dict[int, int] = {}

        for room_num in range(1, 8):
            if comps_dict[4][comp].round_num[str(room_num)]:
                uses_room[room_num] = len(
                    comps_dict[4][comp].round_num[str(room_num)],
                )
                avg_round.append(
                    statistics.mean(
                        comps_dict[4][comp].round_num[str(room_num)],
                    ),
                )

        comps_dict[4][comp].is_count_round = True
        comps_dict[4][comp].is_count_round_print = True
        if (rooms == one_stage) or (da_mode and rooms == ["1-1", "1-2", "1-3"]):
            for uses_room_num in uses_room.values():
                if uses_room_num < 20:
                    comps_dict[4][comp].is_count_round = False
                if uses_room_num < 3:
                    comps_dict[4][comp].is_count_round_print = False
        elif len(rooms) == 1:
            if comps_dict[4][comp].uses < 20:
                comps_dict[4][comp].is_count_round = False
            if comps_dict[4][comp].uses < 3:
                comps_dict[4][comp].is_count_round_print = False

        rounded_avg_round: float
        if avg_round:
            rounded_avg_round = round(statistics.mean(avg_round))
        else:
            rounded_avg_round = DEFAULT_ROUND

        if total == 0:
            print(comps_dict[4][comp].uses)
        app = round(comps_dict[4][comp].uses / total, 2)
        comps_dict[4][comp].app_rate = app
        comps_dict[4][comp].round = rounded_avg_round
        comps_dict[4][comp].usage_rate = 0
        comps_dict[4][comp].own_rate = 0
        rates.append(app)
    rates.sort(reverse=True)
    for comp in comps_dict[4]:
        comps_dict[4][comp].app_rank = rates.index(comps_dict[4][comp].app_rate) + 1


def duo_usages(
    comps: list[Composition],
    players: dict[str, dict[str, PlayerPhase]],
    usage: dict[int, dict[str, cu.CharUsageData]],
    archetype: str,
    rooms: list[str],
) -> None:
    """Calculate duo usage."""
    duos_dict = used_duos(players, comps, rooms, usage)
    duo_write(duos_dict, usage, "duo_usages", archetype)


def used_duos(
    players: dict[str, dict[str, PlayerPhase]],
    comps: list[Composition],
    rooms: list[str],
    usage: dict[int, dict[str, cu.CharUsageData]],
    phase: str = RECENT_PHASE,
) -> dict[str, dict[str, cu.RoundApp]]:
    """Return dictionary of all the duos used and how many times they were used."""
    duos_dict: dict[tuple[str, str], cu.RoundApp] = {}

    for comp in comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        whale_comp = False
        cur_room = next(iter(str(comp.room).split("-")))
        for char in comp.characters:
            if CHARACTERS[char]["availability"] == "Limited S":
                if comp.char_cons:
                    if comp.char_cons[char] > 0:
                        whale_comp = True
                elif (
                    char in players[phase][comp.player].owned
                    and players[phase][comp.player].owned[char].cons > 0
                ):
                    whale_comp = True

        # Permutate the duos, for example if Ganyu and Xiangling are used,
        # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
        duos = list(permutations(comp.characters, 2))
        for duo in duos:
            is_triple_dps = False

            if duo not in duos_dict:
                duos_dict[duo] = cu.RoundApp()
            duos_dict[duo].app_flat += 1

            if is_triple_dps and "Duos check" in run_commands:
                continue
            if not whale_comp:
                duos_dict[duo].round_list[cur_room].append(
                    comp.round_num,
                )

    sorted_duos = sorted(duos_dict.items(), key=lambda t: t[1].app_flat, reverse=True)
    duos_dict = dict(sorted_duos)

    return_duos: dict[str, dict[str, cu.RoundApp]] = {}
    for duo in duos_dict:
        cur_duo = duos_dict[duo]
        if usage[4][duo[0]].app_flat > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            cur_duo.app = round(cur_duo.app_flat * 100 / usage[4][duo[0]].app_flat, 2)
            cur_duo.app_flat = 0
            avg_round: list[float] = []
            for room_num in range(1, 8):
                if cur_duo.round_list[str(room_num)]:
                    avg_round += cur_duo.round_list[str(room_num)]
            if avg_round:
                cur_duo.round = round(statistics.mean(avg_round))
            else:
                cur_duo.round = DEFAULT_ROUND
            if duo[0] not in return_duos:
                return_duos[duo[0]] = {}
            return_duos[duo[0]][duo[1]] = cur_duo

    return return_duos


def char_usages(
    rooms: list[str],
    filename: str = "char_usages",
    info_char: bool = False,
) -> tuple[
    dict[int, dict[str, cu.CharUsageData]],
    dict[int, dict[str, cu.CharUsageData]],
]:
    """Calculate character usage."""
    app = cu.appearances(all_players, chambers=rooms, info_char=info_char)
    chars_dict, boos_dict = cu.usages(app, past_phase, chambers=rooms)
    if (not da_mode and rooms == one_stage) or da_mode:
        char_usages_write(chars_dict[4], filename, archetype)
        boo_usages_write(boos_dict[4], "bangboo_" + filename, archetype)
    return (chars_dict, boos_dict)


def comp_usages_write(
    comps_dict: list[dict[tuple[str, ...], CompUsage]],
    filename: str,
    floor: int,
    info_char: bool,
    sort_app: bool,
) -> None:
    """Write comp usage."""
    out_json: list[dict[str, str | float]] = []
    out_comps: list[dict[str, str | int]] = []
    outvar_comps: list[dict[str, str | int]] = []
    var_comps: list[dict[str, str | int]] = []
    variations: dict[str, int] = {}
    threshold = app_rate_threshold if sort_app else app_rate_threshold_round

    if sort_app:
        comps_dict[4] = dict(
            sorted(
                comps_dict[4].items(),
                key=lambda t: t[1].app_rate,
                reverse=True,
            ),
        )
    comps_dict[4] = dict(
        sorted(
            comps_dict[4].items(),
            key=lambda t: t[1].round,
            reverse=da_mode,
        ),
    )
    comp_names: list[str] = []
    dual_comp_names: list[str] = []

    for comp in comps_dict[4]:
        if info_char and filename not in comp:
            continue
        cur_comp = comps_dict[4][comp]
        comp_name = cur_comp.comp_name
        dual_comp_name = cur_comp.dual_comp_name
        alt_comp_name = cur_comp.alt_comp_name
        # Only one variation of each comp name is included,
        # unless if it's used for a character's infographic
        if (
            (
                comp_name not in comp_names
                and comp_name not in dual_comp_names
                and dual_comp_name not in comp_names
                and alt_comp_name not in comp_names
                and cur_comp.round not in {1, 0}
            )
            or comp_name == "-"
            or info_char
        ):
            if sort_app:
                top_comps_app[comp_name] = cur_comp.app_rate
            if cur_comp.is_count_round and (
                cur_comp.app_rate >= threshold
                or (info_char and cur_comp.app_rate > char_app_rate_threshold)
            ):
                temp_comp_name = alt_comp_name if alt_comp_name != "-" else comp_name

                out_comps_append: dict[str, str | int] = {
                    "comp_name": temp_comp_name,
                    "char_1": comp[0],
                    "char_2": comp[1],
                    "char_3": comp[2],
                    "app_rate": str(
                        cur_comp.app_rate,
                    )
                    + "%",
                    "avg_round": str(cur_comp.round),
                }

                if info_char:
                    if comp_name not in comp_names:
                        variations[comp_name] = 1
                        out_comps_append["variation"] = variations[comp_name]
                    else:
                        variations[comp_name] += 1
                        out_comps_append["variation"] = variations[comp_name]

                out_comps_append["whale_count"] = str(
                    len(cur_comp.whale_count),
                )
                out_comps_append["app_flat"] = str(
                    len(cur_comp.players),
                )
                out_comps_append["uses"] = str(
                    cur_comp.uses,
                )

                if info_char:
                    if comp_name not in comp_names:
                        out_comps.append(out_comps_append)
                    else:
                        var_comps.append(out_comps_append)
                else:
                    out_comps.append(out_comps_append)

                if comp_name != "-":
                    comp_names.append(comp_name)
                if dual_comp_name != "-":
                    dual_comp_names.append(dual_comp_name)
                if alt_comp_name != "-":
                    comp_names.append(alt_comp_name)

        elif comp_name in comp_names:
            temp_comp_name = alt_comp_name if alt_comp_name != "-" else comp_name
            outvar_comps_append: dict[str, str | int] = {
                "comp_name": temp_comp_name,
                "char_1": comp[0],
                "char_2": comp[1],
                "char_3": comp[2],
            }
            outvar_comps_append["app_rate"] = str(cur_comp.app_rate) + "%"
            outvar_comps_append["avg_round"] = str(cur_comp.round)
            outvar_comps.append(outvar_comps_append)
        if not info_char and (
            cur_comp.is_count_round_print and (cur_comp.app_rate >= json_threshold)
        ):
            out = name_filter(list(comp), mode="out")
            for i in range(3):
                out[i] = slugify(out[i])
                if out[i] in slug:
                    out[i] = slug[out[i]]
            out_json_dict: dict[str, str | float] = {
                "char_one": out[0],
                "char_two": out[1],
                "char_three": out[2],
            }
            out_json_dict["app_rate"] = cur_comp.app_rate
            out_json_dict["rank"] = cur_comp.app_rank
            out_json_dict["avg_round"] = cur_comp.round
            out_json_dict["star_num"] = str(4)
            out_json.append(out_json_dict)

    if info_char:
        out_comps += var_comps

    if archetype != "all":
        filename = filename + "_" + archetype

    if not (sort_app):
        filename = filename + "_rounds"

    if whale_only:
        filename = filename + "_C1"
    elif f2p_only:
        filename = filename + "_E0S0"

    if floor:
        with open(
            "../comp_results/comps_usage_" + filename + ".csv",
            "w",
            newline="",
        ) as f:
            csv_writer = csv.writer(f)
            for comps in out_comps:
                csv_writer.writerow(comps.values())

    if not info_char and sort_app:
        all_comps_json[filename] = out_json.copy()
        with open("../comp_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json, indent=2))


def duo_write(
    duos_dict: dict[str, dict[str, cu.RoundApp]],
    usage: dict[int, dict[str, cu.CharUsageData]],
    filename: str,
    archetype: str,
) -> None:
    """Write duo usage."""
    out_duos: list[dict[str, str | float]] = []
    for char, char_duo in duos_dict.items():
        duo_keys = list(char_duo.keys())
        if usage[4][char].app_flat > 0:
            out_duos_append = {
                "char": char,
                "app": usage[4][char].app,
            }
            for i in range(duo_dict_len):
                j = str(i + 1)
                if i < len(char_duo):
                    duo_char = char_duo[duo_keys[i]]
                    out_duos_append["char_" + j] = duo_keys[i]
                    out_duos_append["app_rate_" + j] = str(duo_char.app) + "%"
                    out_duos_append["avg_round_" + j] = duo_char.round
                    out_duos_append["app_flat_" + j] = duo_char.app_flat
                else:
                    out_duos_append["char_" + str(i + 1)] = "-"
                    out_duos_append["app_rate_" + str(i + 1)] = "0.00%"
                    out_duos_append["avg_round_" + str(i + 1)] = 0.00
                    out_duos_append["app_flat_" + str(i + 1)] = 0
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["app"], reverse=True)

    if archetype != "all":
        filename = filename + "_" + archetype
    count = 0
    out_duos_check: dict[str, dict[str, dict[str, str | float]]] = {}
    out_duos_exclu: dict[str, dict[str, dict[str, str | float]]] = {}

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        for duos in out_duos:
            duo_char = str(duos["char"])
            out_duos_check[duo_char] = {}
            out_duos_exclu[duo_char] = {}
            if count == 0:
                temp_duos = ["char", "app"]
                for i in range(10):
                    temp_duos += [
                        "char_" + str(i + 1),
                        "app_rate_" + str(i + 1),
                        "avg_round_" + str(i + 1),
                    ]
                csv_writer.writerow(temp_duos)
                count += 1
            temp_duos = [
                duo_char,
                duos["app"],
            ]
            for i in range(10):
                temp_duos += [
                    duos["char_" + str(i + 1)],
                    duos["app_rate_" + str(i + 1)],
                    duos["avg_round_" + str(i + 1)],
                ]
            csv_writer.writerow(temp_duos)
            for i in range(duo_dict_len):
                j = str(i + 1)
                duo_app_j = float(str(duos["app_rate_" + j])[:-1])
                duo_round_j = float(duos["avg_round_" + j])
                duo_j = str(duos["char_" + j])
                if (
                    duo_app_j >= 1
                    and float(duos["app_flat_" + j]) >= 10
                    and (
                        (duo_round_j < usage[4][duo_j].round)
                        or (duo_round_j < usage[4][duo_char].round)
                    )
                    and usage[4][duo_j].round != 1
                    and usage[4][duo_j].round != 0
                ):
                    out_duos_check[duo_char][duo_j] = {
                        "app": duo_app_j,
                        "avg_round": duo_round_j,
                    }

    if "Duos check" in run_commands:
        char_names = list(CHARACTERS.keys())
        out_dd: dict[frozenset[str], dict[str, str | float]] = {}
        out_dd_list: list[list[str]] = []
        for char_i in char_names:
            for char_j in char_names:
                is_char_i_dps = CHARACTERS[char_i][
                    "role"
                ] == "Damage Dealer" or char_i in [
                    "Sampo",
                    "Black Swan",
                    "Luka",
                    "Guinaifen",
                ]
                is_char_j_dps = CHARACTERS[char_j][
                    "role"
                ] == "Damage Dealer" or char_j in [
                    "Sampo",
                    "Black Swan",
                    "Luka",
                    "Guinaifen",
                ]
                if is_char_i_dps and is_char_j_dps:
                    if char_j not in out_duos_check:
                        continue
                    if char_i not in out_duos_check:
                        continue
                    if char_i in out_duos_check[char_j]:
                        out_dd_list.append([char_j, char_i])
                        out_i_j = out_duos_check[char_i][char_j]
                        out_j_i = out_duos_check[char_j][char_i]
                        if char_j in out_duos_check[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(out_i_j["app"]),
                                "char_j": char_j,
                                "char_j_app": str(out_j_i["app"]),
                                "avg_round": str(
                                    out_i_j["avg_round"],
                                ),
                            }
                        elif char_j in out_duos_exclu[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_exclu[char_i][char_j]["app"],
                                ),
                                "char_j": char_j,
                                "char_j_app": str(out_j_i["app"]),
                                "avg_round": str(
                                    out_duos_exclu[char_i][char_j]["avg_round"],
                                ),
                            }

        sorted_out_dd = sorted(
            out_dd.items(),
            key=lambda t: t[1]["char_i"],
            reverse=True,
        )
        out_dd = dict(sorted_out_dd)

        with open("../char_results/duo_check.csv", "w", newline="") as f:
            csv_writer = csv.writer(f)
            for out_dd_print in out_dd_list:
                csv_writer.writerow(out_dd_print)
        for out_dd_print in out_dd:
            print(
                str(out_dd[out_dd_print]["char_i"])
                + ", "
                + str(out_dd[out_dd_print]["char_i_app"])
                + ", "
                + str(out_dd[out_dd_print]["char_j"])
                + ", "
                + str(out_dd[out_dd_print]["char_j_app"])
                + ", "
                + str(out_dd[out_dd_print]["avg_round"]),
            )
        if __name__ == "__main__" and notification.notify:
            notification.notify(
                title="Finished",
                message="Finished executing comp_rates",
                # displaying time
                timeout=2,
            )
            # waiting time
            time.sleep(1)
        sys_exit()

    for i in range(len(out_duos)):
        for duo_value in ["char"] + [f"char_{i}" for i in range(1, 31)]:
            if out_duos[i][duo_value]:
                out_duos[i][duo_value] = slugify(str(out_duos[i][duo_value]))
                if out_duos[i][duo_value] in slug:
                    out_duos[i][duo_value] = slug[out_duos[i][duo_value]]
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_duos, indent=2))


def boo_usages_write(
    chars_dict: dict[str, cu.CharUsageData],
    filename: str,
    archetype: str,
) -> None:
    """Write bangboos usage."""
    out_chars: list[dict[str, str | int | float]] = []
    out_chars_csv: list[dict[str, str | int | float]] = []
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1].app, reverse=True))
    for char, cur_char in chars_dict.items():
        out_chars_append: dict[str, str | int | float] = {
            "char": char,
            "app_rate": str(cur_char.app) + "%",
            "avg_round": str(cur_char.round),
            "rarity": cur_char.rarity,
            "diff": str(cur_char.diff) + "%",
            "diff_rounds": str(cur_char.diff_rounds),
        }
        for i in ["app_rate", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if whale_only:
        filename = filename + "_C1"
    elif f2p_only:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "diff"]
    iterate_value_round = ["avg_round", "diff_rounds"]

    for i in range(len(out_chars)):
        out_chars[i]["char"] = slugify(str(out_chars[i]["char"]))
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if (
                str(out_chars[i][value])[:-1]
                .replace(".", "")
                .replace("-", "")
                .isnumeric()
            ):
                out_chars[i][value] = float(str(out_chars[i][value])[:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if str(out_chars[i][value]).replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = round(float(out_chars[i][value]))
            else:
                out_chars[i][value] = DEFAULT_ROUND
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        count = 0
        for chars in out_chars_csv:
            if count == 0:
                header = chars.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(chars.values())


def char_usages_write(
    chars_dict: dict[str, cu.CharUsageData],
    filename: str,
    archetype: str,
) -> None:
    """Write character usage."""
    out_chars: list[dict[str, str | int | float]] = []
    out_chars_csv: list[dict[str, str | int | float]] = []
    weap_len = 10
    arti_len = 10
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1].app, reverse=True))
    for char, cur_char in chars_dict.items():
        out_chars_append: dict[str, str | int | float] = {
            "char": char,
            "app_rate": str(cur_char.app) + "%",
            "avg_round": str(cur_char.round),
            "std_dev_round": str(cur_char.std_dev_round),
            "q1_round": str(cur_char.q1_round),
            "role": cur_char.role,
            "rarity": cur_char.rarity,
            "diff": str(cur_char.diff) + "%",
            "diff_rounds": str(cur_char.diff_rounds),
        }
        for i in ["app_rate", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        if list(cur_char.weapons):
            for i in range(weap_len):
                if i < len(list(cur_char.weapons)):
                    out_chars_append["weapon_" + str(i + 1)] = list(cur_char.weapons)[i]
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = (
                        str(list(cur_char.weapons.values())[i].app) + "%"
                    )
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        list(cur_char.weapons.values())[i].round,
                    )
                else:
                    out_chars_append["weapon_" + str(i + 1)] = ""
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        DEFAULT_ROUND,
                    )
            for i in range(arti_len):
                if i < len(list(cur_char.artifacts)):
                    arti_name = list(cur_char.artifacts)[i]
                    out_chars_append["artifact_" + str(i + 1)] = arti_name
                    arti_name = arti_name.split(", ")
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = arti_name[0]
                    if len(arti_name) > 1:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = arti_name[1]
                        if len(arti_name) > 2:
                            out_chars_append["artifact_" + str(i + 1) + "_3"] = (
                                arti_name[2]
                            )
                        else:
                            out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                    else:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = (
                        str(list(cur_char.artifacts.values())[i].app) + "%"
                    )
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        list(cur_char.artifacts.values())[i].round,
                    )
                else:
                    out_chars_append["artifact_" + str(i + 1)] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        DEFAULT_ROUND,
                    )
            for i in range(7):
                out_chars_append["app_" + str(i)] = (
                    str(next(iter(list(cur_char.cons_usage.values())[i].values())))
                    + "%"
                )
                out_chars_append["round_" + str(i)] = str(
                    list(list(cur_char.cons_usage.values())[i].values())[3],
                )
                if out_chars_append["app_" + str(i)] == "-%":
                    out_chars_append["app_" + str(i)] = "-"
            out_chars_append["cons_avg"] = cur_char.cons_avg
            out_chars_append["sample"] = cur_char.sample
            out_chars_append["sample_app_flat"] = cur_char.sample_app_flat
        else:
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = ""
                out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["weapon_" + str(i + 1) + "_round"] = str(DEFAULT_ROUND)
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = ""
                out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_3"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                    DEFAULT_ROUND,
                )
            for i in range(7):
                out_chars_append["app_" + str(i)] = "0.0%"
                out_chars_append["round_" + str(i)] = str(DEFAULT_ROUND)
            out_chars_append["cons_avg"] = cur_char.cons_avg
            out_chars_append["sample"] = cur_char.sample
            out_chars_append["sample_app_flat"] = cur_char.sample_app_flat
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if whale_only:
        filename = filename + "_C1"
    elif f2p_only:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "diff"]
    iterate_value_round = ["avg_round", "std_dev_round", "q1_round", "diff_rounds"]
    iterate_name_arti: list[str] = []
    for i in range(weap_len):
        iterate_value_app.append("weapon_" + str(i + 1) + "_app")
        iterate_value_round.append("weapon_" + str(i + 1) + "_round")
    for i in range(arti_len):
        iterate_value_app.append("artifact_" + str(i + 1) + "_app")
        iterate_value_round.append("artifact_" + str(i + 1) + "_round")
    for i in range(7):
        iterate_value_app.append("app_" + str(i))
        iterate_value_round.append("round_" + str(i))

    for i in range(len(out_chars)):
        # for i in range(7):
        out_chars[i]["char"] = slugify(str(out_chars[i]["char"]))
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if (
                str(out_chars[i][value])[:-1]
                .replace(".", "")
                .replace("-", "")
                .isnumeric()
            ):
                out_chars[i][value] = float(str(out_chars[i][value])[:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if str(out_chars[i][value]).replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = round(float(out_chars[i][value]))
            else:
                out_chars[i][value] = DEFAULT_ROUND
        for value in iterate_name_arti:
            if out_chars[i][value]:
                out_chars[i][value] = (
                    str(out_chars[i][value]).replace(".", "").replace("-", "")
                )
            else:
                out_chars[i][value] = DEFAULT_ROUND
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    with open("../char_results/" + filename + ".csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        count = 0
        for chars in out_chars_csv:
            if count == 0:
                header = chars.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(chars.values())


def name_filter(comp: list[str], mode: str = "out") -> list[str]:
    """Filter names."""
    if mode == "out":
        return comp
    return []


main()
