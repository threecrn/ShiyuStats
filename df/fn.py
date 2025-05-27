def to_list(s: str):
    if s and s != '':
        return s.split(',')
    return None

agent_aliases = {
    'SAnby': 'Soldier 0 - Anby',
    'Sanby': 'Soldier 0 - Anby',
    'Astra': 'Astra Yao',
}

def map_agent_list(l: list):
    return [a if not a in agent_aliases else agent_aliases[a] for a in l]
