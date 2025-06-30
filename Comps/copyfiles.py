import shutil
from os import listdir, mkdir, path

from comp_rates_config import RECENT_PHASE, da_mode
from send2trash import send2trash

suffix = ""
sd_suffix = ""
if da_mode:
    suffix = "_da"
    sd_suffix = "da"
else:
    sd_suffix = "sd"

RECENT_PHASE_PF = RECENT_PHASE + suffix

source_dirs = [
    "../char_results/" + RECENT_PHASE_PF,
    "../comp_results/" + RECENT_PHASE_PF + "/json",
]

target_dir: str = ""
temp_target_dir: str = ""

for source_dir in source_dirs:
    if "comp_results" in source_dir:
        target_dir = "../web_results/" + sd_suffix + "/comps"
    else:
        target_dir = "../web_results/" + sd_suffix + "/chars"

    file_names = listdir(source_dir)
    if path.exists(target_dir):
        send2trash(target_dir)
    mkdir(target_dir)
    for file_name in file_names:
        if "comp_results" in source_dir or (
            file_name == "duo_usages.json"
            or file_name == ("demographic_collect" + suffix + ".json")
            or (file_name == "builds.json" and (RECENT_PHASE + "_da") in source_dir)
            or (
                file_name == "bosses_name.csv"
                and (RECENT_PHASE + "_da") not in source_dir
            )
        ):
            if file_name in ["builds.json", "bosses_name.csv"]:
                temp_target_dir: str = target_dir
                target_dir = "../web_results"
            copyfrom = path.join(source_dir, file_name)
            copyto = path.join(target_dir, file_name)
            shutil.copyfile(copyfrom, copyto)
            if file_name in ["builds.json", "bosses_name.csv"]:
                target_dir = temp_target_dir

if da_mode:
    shutil.make_archive("../results", "zip", "../web_results")
