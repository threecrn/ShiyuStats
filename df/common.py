import re
import logging
import argparse

def to_list(s: str):
    if s and s != '':
        return s.split(',')
    return None

boss_aliases = {
    'UCC':     'Unknown Corruption Complex',
    'Butcher': 'Dead End Butcher',
    'Typhoon': 'Autonomous Assault Unit - Typhon Destroyer',
    'Pompey':  'Corrupted Overlord - Pompey',
    'Bringer': 'Sacrifice - Bringer',
    'NPompey': 'Notorious - Pompey',
    'Marionette': 'Notorious - Marionette',
    'NButcher':   'Notorious - Dead End Butcher',
}

da_boss_shortended = {
    name:alias for alias,name in boss_aliases.items()
}

agent_aliases = {
    'SAnby': 'Soldier 0 - Anby',
    'S0':    'Soldier 0 - Anby',
    'Sanby': 'Soldier 0 - Anby',
    'Astra': 'Astra Yao',
    'S11':   'Soldier 11',
    'ZY':    'Zhu Yuan',
}

agent_shortended = {
    name:alias for alias,name in agent_aliases.items()
}

def series_shorten_da_boss(ser):
    return ser.map(da_boss_shortended).fillna(ser)

def series_shorten_agent(ser):
    return ser.map(agent_shortended).fillna(ser)

def add_query_arguments(parser):
    parser.add_argument('-v', '--version', type=str, default='1.7.1', help="game version (e.g. 1.7.1)")

    parser.add_argument('--team', help="comma separated list of team members (e.g. 'Miyabi,Yanagi'). May include mindscape constraints: 'Miyabi<=M2' means Miyabi up to M2. May exclude certain agents: '!Astra' means no team with Astra Yao in it.")
    
    parser.add_argument('--roaster', help="comma separated list of roaster members (e.g. 'Miyabi,Yanagi,Lucy,Nicole'). May include mindscape constraints: 'Miyabi<=M2' means Miyabi up to M2.")

    parser.add_argument('--shorten', default=True, action=argparse.BooleanOptionalAction, help="use shortened boss/agent names")
    
    #parser.add_argument('--output-format', default='df', choices=['df'])
    #parser.add_argument('--include-columns', default=None)
    #parser.add_argument('--exclude-columns', default=None)
    parser.add_argument('--pandas-max-rows', default=None, type=int)
    #parser.add_argument('--pandas-line-width', default=None, type=int)
    parser.add_argument('--pandas-query', default=None, help='pandas query to filter result before output (e.g. "floor in (1,2) and bangboo == \'Rocketboo\'")')
    parser.add_argument('--pandas-order', default=None, help='comma separated list of columns to sort output by')
    

def map_agent_expr(a: str):
    pat_not_agent = r'^[!](?P<agent>.+)$'
    pat_rank_lt = r'^(?P<agent>.+?)[<][Mm](?P<rank>[1-6])$'
    pat_rank_le = r'^(?P<agent>.+?)[<][=][Mm](?P<rank>[1-6])$'
    pat_rank_gt = r'^(?P<agent>.+?)[>][Mm](?P<rank>[0-5])$'
    pat_rank_ge = r'^(?P<agent>.+?)[>][=][Mm](?P<rank>[0-5])$'
    pat_rank_eq = r'^(?P<agent>.+?)[=]{1,2}[Mm](?P<rank>[0-6])$'
    if m := re.match(pat_not_agent, a):
        return (m.group('agent'), ('not',))
    elif m := re.match(pat_rank_lt, a):
        return (m.group('agent'), ('lt', int(m.group('rank'))))
    elif m := re.match(pat_rank_le, a):
        return (m.group('agent'), ('le', int(m.group('rank'))))
    elif m := re.match(pat_rank_gt, a):
        return (m.group('agent'), ('gt', int(m.group('rank'))))
    elif m := re.match(pat_rank_ge, a):
        return (m.group('agent'), ('ge', int(m.group('rank'))))
    elif m := re.match(pat_rank_eq, a):
        return (m.group('agent'), ('eq', int(m.group('rank'))))
    return (a,None)

def map_agent_list(l: list):
    return [
        a if not a[0] in agent_aliases
        else (agent_aliases[a[0]],a[1])
        for a in l
    ]

def team_query(team: list):
    def render_or(agent,slot,cond):
        if cond is None:
            return f"(ch{slot} == '{agent}')"
        else:
            if cond[0] == 'lt':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank < {cond[1]})"
            elif cond[0] == 'le':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank <= {cond[1]})"
            elif cond[0] == 'gt':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank > {cond[1]})"
            elif cond[0] == 'ge':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank >= {cond[1]})"
            elif cond[0] == 'eq':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank == {cond[1]})"
        return f"(ch{slot} == '{agent}')"
    
    return ' and '.join([
        '(' + " or ".join([render_or(m[0], i, m[1]) for i in range(1,4)]) + ')'
        if (m[1] is None or m[1][0] != 'not')
        else
        '(' + " and ".join([f"ch{i} != '{m[0]}'" for i in range(1,4)]) + ')'
        for m in team
    ])

def team_to_query(s: str) -> str:
    l = to_list(s)
    logging.debug(f"l={l}")
    l = [map_agent_expr(a) for a in l]
    logging.debug(f"l={l}")
    team = map_agent_list(l)
    logging.debug(f"team={team}")
    query = team_query(team)
    logging.debug(f"query={query}")
    return query

def roaster_query(roaster: list):
    def render(agent,slot,cond):
        if cond is None:
            return f"(ch{slot} == '{agent}')"
        else:
            if cond[0] == 'lt':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank < {cond[1]})"
            elif cond[0] == 'le':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank <= {cond[1]})"
            elif cond[0] == 'gt':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank > {cond[1]})"
            elif cond[0] == 'ge':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank >= {cond[1]})"
            elif cond[0] == 'eq':
                return f"(ch{slot} == '{agent}' and ch{slot}_rank == {cond[1]})"
        return f"(ch{slot} == '{agent}')"
    
    return ' and '.join([
        '(' + " or ".join([render(m[0], i, m[1]) for m in roaster]) + ')'
        for i in range(1,4)
    ])

def roaster_to_query(s: str) -> str:
    l = to_list(s)
    logging.debug(f"l={l}")
    l = [map_agent_expr(a) for a in l]
    logging.debug(f"l={l}")
    roaster = map_agent_list(l)
    logging.debug(f"roaster={roaster}")
    query = roaster_query(roaster)
    logging.debug(f"query={query}")
    return query
