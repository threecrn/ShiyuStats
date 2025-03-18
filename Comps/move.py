from os import listdir, path, mkdir
import shutil

from comp_rates_config import RECENT_PHASE, da_mode

suffix = ""
if da_mode:
    suffix = "_da"
RECENT_PHASE_PF = RECENT_PHASE + suffix

source_dirs = [
    "../char_results",
    "../comp_results",
    "../comp_results/json",
    # "../mihomo",
    # "../mihomo/results_real",
]

for source_dir in source_dirs:
    if source_dir == "../comp_results/json":
        target_dir = "../comp_results/" + RECENT_PHASE_PF + "/json"
    elif source_dir == "../mihomo":
        target_dir = "../mihomo/results_real"
    elif source_dir == "../mihomo/results_real":
        target_dir = source_dir + "/" + RECENT_PHASE
    else:
        target_dir = source_dir + "/" + RECENT_PHASE_PF

    file_names = listdir(source_dir)
    if not path.exists(target_dir):
        mkdir(target_dir)
    for file_name in file_names:
        if (source_dir == "../mihomo" and file_name.startswith("output")) or (
            source_dir != "../mihomo"
            and file_name.endswith(tuple([".json", ".csv"]))
            and (
                "demographic_collect" not in file_name
                or file_name == ("demographic_collect" + suffix + ".json")
            )
        ):
            shutil.move(path.join(source_dir, file_name), target_dir)
