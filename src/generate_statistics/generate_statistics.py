import json
import glob
import re
import pandas as pd

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
                'RUNNING': 'running', 'SPRAY':'spraying', 'STRIKING':'striking', 'THROWING':'throwing'}

    res = {all_keys[k]: v for k,v in res.items()}

    # remove unwanted detections
    if 'pepperSpray' in res.keys():
        del res['pepperSpray']
    
    # calculate violent actions
    violent_actions = ['striking', 'brawling', 'restraining', 'throwing']
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

def generate_csv_and_json(video_id):
    """This function can only run after a combined and a stats json have been generated"""

    with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
        combined_data = json.load(f)
    with open(f"temp_videodata_storage/{video_id}_stats.json") as f:
        stats_data = json.load(f)
    
    #extract all classes with detections
    all_classes = list(stats_data['table'].keys())
    try:
        all_classes.remove('forcefulActions')
    except:
        pass
    
    print(all_classes)
    df = pd.DataFrame()

    for cla in all_classes:
        #go through stats chart
        data = {f'{cla} Total': stats_data['table'][cla]}
        df[f'{cla} Total'] = stats_data['table'][cla]

        # transform names from stat chart into names inside combined
        i = 0
        # add spaces
        for ind, c in enumerate(cla):
            if c.isupper() == True:
                cla = cla[0:ind + i] + ' ' + cla[ind+i:]
                i +=1
        # add capitals
        cla = cla.title()

        # g
                
        print(cla)




        df[f'{cla} Timestamps'] = 0
    print(df)
#generate_csv_and_json('IMG_1509')
