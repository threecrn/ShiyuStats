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

def load_char(ver='1.7.1'):
    fpath = basedir / 'data/raw_csvs' / f"{ver}_char.csv"
    logging.debug(f"load_char fpath={fpath}")
    df = pd.read_csv(fpath)
    logging.debug(f"load_char df=[\n{df}\n]")
    return df

def load_shiyu(ver='1.7.1'):
    fpath = basedir / 'data/raw_csvs' / f"{ver}.csv"
    logging.debug(f"load_shiyu fpath={fpath}")
    df = pd.read_csv(fpath, dtype={
        'ch1_rank': 'Int8',
        'ch2_rank': 'Int8',
        'ch3_rank': 'Int8',
    })
    logging.debug(f"load_shiyu df=[\n{df}\n]")
    return df

def cmd_show(args):
    logging.debug("cmd_show args={args}")
    df = load_shiyu(args.version)
    if args.floor:
        df = df[df["floor"] == args.floor]
    if args.side:
        df = df[df["node"] == args.side]
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
    pd.set_option('display.max_rows', args.pandas_max_rows)
    if args.shorten:
        df['ch1'] = common.series_shorten_agent(df['ch1'])
        df['ch2'] = common.series_shorten_agent(df['ch2'])
        df['ch3'] = common.series_shorten_agent(df['ch3'])
    if args.exclude_columns:
        df = df.drop(common.to_list(args.exclude_columns))
    print(df)

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
        description="ZZZ Shiyu data tool",
        epilog=f"example: {sys.argv[0]} show --version=1.6.1 --floor=7 --side=1 --team=Evelyn,Koleda --pandas-order=time"
    )
    parser.add_argument('--debug',  action="store_true", help='debug mode')
    parser.add_argument('command', choices=[name[4:] for name in command_map.keys()])
    parser.add_argument('--floor', type=int, help="only specific shiyu floor [1..7]")
    parser.add_argument('--side', type=int, help="only specific shiyu side [1..2]")

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
