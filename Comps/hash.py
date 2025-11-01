# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
"""Hash function for comp rates."""

from collections.abc import Iterator
from itertools import count

from comp_rates_config import RECENT_PHASE
from pandas import read_csv

# Create sequential ID generator
id_generator: Iterator[int] = count(1000000)  # Start at 1,000,000 (7 digits)
pass_hash = {}

df_char = read_csv(
    "../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv",
    encoding="cp1252",
).convert_dtypes()
df_spiral = read_csv(
    "../data/raw_csvs_real/" + RECENT_PHASE + ".csv",
    encoding="cp1252",
).convert_dtypes()
df_spiral_da = read_csv(
    "../data/raw_csvs_real/" + RECENT_PHASE + "_da.csv",
    encoding="cp1252",
).convert_dtypes()
df_stats = read_csv(
    "../enka.network/results_real/" + RECENT_PHASE + "/output1.csv",
    encoding="cp1252",
).convert_dtypes()

for i in df_char["uid"].unique():
    pass_hash[i] = next(id_generator)
for i in df_spiral["uid"].unique():
    if i not in pass_hash:
        pass_hash[i] = next(id_generator)
for i in df_spiral_da["uid"].unique():
    if i not in pass_hash:
        pass_hash[i] = next(id_generator)

df_char["uid"] = df_char["uid"].replace(pass_hash)
df_spiral["uid"] = df_spiral["uid"].replace(pass_hash)
df_spiral_da["uid"] = df_spiral_da["uid"].replace(pass_hash)
df_stats["uid"] = df_stats["uid"].replace(pass_hash)
print("csv done")

df_char.to_csv("../data/raw_csvs/" + RECENT_PHASE + "_char.csv", index=False)
df_spiral.to_csv("../data/raw_csvs/" + RECENT_PHASE + ".csv", index=False)
df_spiral_da.to_csv("../data/raw_csvs/" + RECENT_PHASE + "_da.csv", index=False)
df_stats.to_csv("../enka.network/results/" + RECENT_PHASE + "_output.csv", index=False)
