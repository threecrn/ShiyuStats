import re
import logging

def to_list(s: str):
    if s and s != '':
        return s.split(',')
    return None

agent_aliases = {
    'SAnby': 'Soldier 0 - Anby',
    'Sanby': 'Soldier 0 - Anby',
    'S0':    'Soldier 0 - Anby',
    'Astra': 'Astra Yao',
    'S11':   'Soldier 11',
    'ZY':    'Zhu Yuan',
}

def map_agent_expr(a: str):
    pat_not_agent = r'^[!](?P<agent>.+)$'
    pat_rank_lt = r'^(?P<agent>.+?)[<](?P<rank>[1-6])$'
    pat_rank_le = r'^(?P<agent>.+?)[<][=](?P<rank>[1-6])$'
    pat_rank_gt = r'^(?P<agent>.+?)[>](?P<rank>[0-5])$'
    pat_rank_ge = r'^(?P<agent>.+?)[>][=](?P<rank>[0-5])$'
    pat_rank_eq = r'^(?P<agent>.+?)[=]{1,2}(?P<rank>[0-6])$'
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
