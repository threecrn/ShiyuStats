#!/usr/bin/python3

import os
import sys
import logging
import argparse
import logging
import pathlib
import pandas as pd

scriptdir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
basedir = scriptdir / '../'

import common

def load_da(ver='1.7.1'):
    fpath = basedir / 'data' / f"{ver}_da.csv"
    logging.debug(f"load_da fpath={fpath}")
    df = pd.read_csv(fpath, dtype={
        'ch1_rank': 'Int8',
        'ch2_rank': 'Int8',
        'ch3_rank': 'Int8',
    })
    logging.debug(f"load_da df=[\n{df}\n]")
    return df

def cmd_show(args) -> None:
    logging.debug("cmd_show args={args}")
    versions = common.to_list(args.version)
    pd.set_option('display.max_rows', args.pandas_max_rows)
    for version in versions:
        df = load_and_filter_version(version, args)
        df['version'] = version
        print(df)

def load_and_filter_version(version, args) -> pd.DataFrame:
    df = load_da(version)
    if args.floor:
        df = df[df["floor"] == args.floor]
    if args.team:
        query = common.team_to_query(args.team)
        logging.debug(f"team query={query}")
        df = df.query(query)
    if args.roaster:
        query = common.roaster_to_query(args.roaster)
        logging.debug(f"roaster query={query}")
        df = df.query(query)
    if args.pandas_query:
        df = df.query(args.pandas_query)
    if args.pandas_order:
        df = df.sort_values(common.to_list(args.pandas_order))
    if args.shorten:
        df['ch1'] = common.series_shorten_agent(df['ch1'])
        df['ch2'] = common.series_shorten_agent(df['ch2'])
        df['ch3'] = common.series_shorten_agent(df['ch3'])
        df['boss'] = common.series_shorten_da_boss(df['boss'])
    def team_string(ch1, ch1_rank, ch2, ch2_rank, ch3, ch3_rank):
        return ",".join([f"{p[0]}M{p[1]}" for p in sorted([i for i in [(ch1,ch1_rank), (ch2,ch2_rank), (ch3,ch3_rank)] if type(i[0]) == str])])
    df['team'] = df.apply(lambda row: team_string(row['ch1'], row['ch1_rank'], row['ch2'], row['ch2_rank'], row['ch3'], row['ch3_rank']), axis=1) #df['ch1'] + 'M' + df['ch1_rank'] # + ',' + df['ch2'] + 'M' + df['ch2_rank'] + ',' + df['ch3'] + 'M' + df['ch3_rank']
    if args.exclude_columns:
        df = df.drop(common.to_list(args.exclude_columns))
    return df

def get_cmd_map():
    import inspect
    return {name:obj
        for name,obj in inspect.getmembers(sys.modules[__name__])
        if (True
            and inspect.isfunction(obj)
            and name.startswith('cmd_')
            and obj.__module__ == __name__
        )
    }

def get_arg_parser():
    command_map = get_cmd_map()
    parser = argparse.ArgumentParser(
        description="ZZZ DA data tool",
        epilog=f"example: {sys.argv[0]} show --version=1.6.1 --floor=3 --team=Evelyn,Koleda --pandas-order=score"
    )
    parser.add_argument('--debug',  action="store_true", help='debug mode')
    parser.add_argument('command', choices=[name[4:] for name in command_map.keys()])
    parser.add_argument('--floor', type=int, help="only specific floor/boss [1..3]")

    common.add_query_arguments(parser)
    
    return parser

def handle_args(argv):
    parser = get_arg_parser()
    global args
    args = parser.parse_args(argv)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("args: %s", args)
    return args


def main():
    args = handle_args(sys.argv[1:])
    command_map = get_cmd_map()
    command_map[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
