import json
import glob

def generate_statistics(video_id):

    with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
        data = json.load(f)
    
    res = dict()
    for sub in data['seconds'].values():
        for key, ele in sub.items():
            res[key] = ele + res.get(key, 0)
    

    #calculate violent actions

    violent_actions = ['striking', 'brawling', 'arresting']
    sum = 0
    for va in violent_actions:
        for key, value in res.items():
            if key == va:
                sum = value + sum
    res['violent_actions'] = sum

    #modify name values
    """
    try:
        res['non_uniformed'] = res.pop('Non Uniformed')
        res['uniformed'] = res.pop('Uniformed')
        res['chemical_smoke'] = res.pop('Chemical Smoke')
        res['riot_shield'] = res.pop('Riot Shield')
        res['baton'] = res.pop('Baton')
        res['restraining'] = res.pop('arresting')
    except Exception as e:
        print(e)
    """


    with open(f"temp_videodata_storage/{video_id}_stats.json", "w") as outfile:
        json.dump(res, outfile)
