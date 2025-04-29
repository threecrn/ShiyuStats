import _thread
import asyncio
import sys
import time
import traceback
from datetime import datetime
from pickle import dump as p_dump
from pickle import load as p_load
from typing import TYPE_CHECKING

import enka  # type: ignore
from enka_config import (
    csv,
    desired_stats_keys,
    drive_data,
    filename,
    json,
    output_keys,
    relics_data,
    substat_keys,
    uids,
)

sys.path.append("../Comps/")
from comp_rates_config import offline_collect, save_to_file

if TYPE_CHECKING:
    from enka.zzz import ShowcaseResponse  # type: ignore

print(len(uids))


class CustomEncoder(json.JSONEncoder):
    def default(self, o: datetime | object) -> str | dict[str, str]:
        if isinstance(o, datetime):
            return o.isoformat()
        elif hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)


def remove_nbsp(lines: list[str | int | float | None]) -> list[str]:
    return [str(line).replace("\xa0", " ") for line in lines]


def jprint(obj: dict[str, str]) -> None:
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def input_thread(input_list: list[bool]) -> None:
    input()
    input_list.append(True)


async def main() -> None:
    async with enka.ZZZClient(enka.zzz.Language.ENGLISH) as client:
        await client.start()
        is_update = input("Update assets? (y/n) ")
        if is_update == "y":
            await client.update_assets()

        # error_uids = []
        writer = csv.writer(open(filename + ".csv", "w", encoding="UTF8", newline=""))
        writer.writerow(output_keys)

        header = [
            "uid",
            "phase",
            "name",
            "level",
            "cons",
            "weapon",
            "element",
            "artifacts",
        ]
        writer_chars = csv.writer(
            open(filename + "_char.csv", "w", encoding="UTF8", newline="")
        )
        writer_chars.writerow(header)

        input_list: list[bool] = []
        _thread.start_new_thread(input_thread, (input_list,))
        uid_iter = -1
        while not input_list and uid_iter < len(uids) - 1:
            uid_iter += 1
            uid = uids[uid_iter]

            i: int = -1
            while i < 5:
                i += 1
                if i == 5:
                    print("error")
                try:
                    print(f"{uid_iter + 1} / {len(uids)} : {uid}, {i}")
                    if offline_collect:
                        with open("data.pkl", "rb") as f:
                            data = p_load(f)
                    else:
                        data: ShowcaseResponse = await client.fetch_showcase(uid)
                        if save_to_file:
                            with open("data.pkl", "wb") as f:
                                p_dump(data, f)
                            with open("data.json", "w") as f:
                                f.write(
                                    json.dumps(
                                        data.__dict__, cls=CustomEncoder, indent=2
                                    )
                                )

                    for character in data.agents:
                        element_name = character.elements[-1]
                        if element_name == "Elec":
                            element_name = "Electric"
                        if element_name == "Physics":
                            element_name = "Physical"
                        line: list[str | int | float | None] = []
                        line_chars: list[str | int | float | None] = []
                        w_engine = character.w_engine
                        line.extend(
                            [
                                uid,
                                data.player.level,
                                character.name,
                                character.level,
                                element_name,
                                w_engine.name if w_engine else "",
                                w_engine.level if w_engine else "",
                            ]
                        )
                        line_chars.extend(
                            [
                                uid,
                                "",
                                character.name,
                                character.level,
                                character.mindscape,
                                w_engine.name if w_engine else "",
                                element_name,
                            ]
                        )

                        for skill in character.skills:
                            line.append(skill.level)
                        desired_stats: dict[str, float] = dict.fromkeys(
                            [
                                key
                                if key != "DMG Bonus"
                                else f"{element_name} DMG Bonus"
                                for key in desired_stats_keys
                            ],
                            0,
                        )

                        for stat in character.stats.values():
                            stat_name = stat.name.replace("\xa0", " ")
                            if stat_name in desired_stats:
                                desired_stats[stat_name] = (
                                    stat.value / 100
                                    if "%" in stat.format
                                    else stat.value
                                )

                        for stat in desired_stats.values():
                            line.append(round(stat, 3))

                        mainstats = {
                            4: "",
                            5: "",
                            6: "",
                        }
                        substats: dict[str, float] = dict.fromkeys(substat_keys, 0)

                        artifacts: dict[str, int] = {}
                        for relic in character.discs:
                            set_id: int = drive_data["Items"][str(relic.id)]["SuitId"]
                            relic_name = relics_data[str(set_id)]["name"].replace(
                                "\xa0", " "
                            )
                            if relic.slot in mainstats:
                                mainstats[relic.slot] = relic.main_stat.name
                            if relic_name not in artifacts:
                                artifacts[relic_name] = 1
                            else:
                                artifacts[relic_name] += 1
                            for stat in relic.sub_stats:
                                stat_name = stat.name.replace("\xa0", " ")
                                if stat_name in substats:
                                    substats[stat_name] += (
                                        stat.value / 100
                                        if "%" in stat.format
                                        else stat.value
                                    )

                        for stat_key in list(substats.keys()):
                            line.append(round(substats[stat_key], 3))

                        for stat_key in list(mainstats.keys()):
                            line.append(mainstats[stat_key])

                        char_set: None | str = None
                        len_artifacts = 0
                        for arti_set in artifacts:
                            if artifacts[arti_set] >= 2:
                                char_set_name = arti_set
                                len_artifacts += 2
                                if artifacts[arti_set] >= 4:
                                    len_artifacts += 2
                                    char_set_name = "4p " + char_set_name
                                if char_set is not None:
                                    if char_set_name < char_set:
                                        char_set = char_set_name + ", " + char_set
                                    else:
                                        char_set += ", " + char_set_name
                                else:
                                    char_set = char_set_name
                        if len_artifacts < 6:
                            if char_set is not None:
                                char_set += ", Flex"
                            else:
                                char_set = "Flex"

                        line.append(char_set)
                        line_chars.append(char_set)

                        writer.writerow(remove_nbsp(line))
                        writer_chars.writerow(remove_nbsp(line_chars))
                    break

                except enka.errors.PlayerDoesNotExistError:
                    print("Player does not exist.")
                    break

                except enka.errors.GameMaintenanceError:
                    print("Game is in maintenance.")
                    break

                except asyncio.exceptions.TimeoutError:
                    print("timeout")
                    time.sleep(1)

                except AttributeError:
                    print(f"{uid}: {traceback.format_exc()}")
                    # print(str(uid) + " Too Many Requests")
                    time.sleep(1)

                except Exception as e:
                    if str(e) == "[429] Too Many Requests":
                        print("[429] Too Many Requests")
                        time.sleep(3)
                    elif "Cannot connect" in str(e):
                        print("Cannot connect")
                        i = 0
                        time.sleep(1)
                    elif str(e) == "User not found.":
                        print("User not found.")
                        break
                    else:
                        print(f"{uid}: {traceback.format_exc()}")
                        # exit()
                        break

        print("\nFinished")
        await client.close()


asyncio.run(main())
