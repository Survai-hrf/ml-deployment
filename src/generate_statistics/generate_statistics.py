import json
import glob
import re

def generate_statistics(video_id):

    with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
        data = json.load(f)
    
    res = dict()
    for sub in data['seconds'].values():
        for key, ele in sub.items():
            res[key] = ele + res.get(key, 0)
    
    #modify name values
    res = {k.upper(): v for k, v in res.items()}
    res = {re.sub(r'[_\s+]', '', k): v for k, v in res.items()}

    all_keys = {'BATON':'baton', 'CHEMICALSMOKE':'chemicalSmoke', 'NONUNIFORMED':'nonUniformed',
                'UNIFORMED':'uniformed', 'RIOTSHIELD':'riotShield', 'PEPPERSPRAY':'pepperSpray', 'GUN': 'gun', 
                'RESTRAINING': 'restraining', 'BRAWLING':'brawling', 'CROWD':'crowd', 'PERSONONGROUND':'personOnGround',
                'RUNNING': 'running', 'SPRAY':'spray', 'STRIKING':'striking', 'THROWING':'throwing'}

    res = {all_keys[k]: v for k,v in res.items()}

    #calculate violent actions

    violent_actions = ['striking', 'brawling', 'restraining']
    sum = 0
    for va in violent_actions:
        for key, value in res.items():
            if key == va:
                sum = value + sum
    res['forcefulActions'] = sum
    final = {}
    final['table'] = res


    with open(f"temp_videodata_storage/{video_id}_stats.json", "w") as outfile:
        json.dump(final, outfile)
