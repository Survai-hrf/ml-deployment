import json

def generate_statistics(video_id):

    with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
        data = json.load(f)
    
    res = dict()
    for sub in data['seconds'].values():
        for key, ele in sub.items():
            res[key] = ele + res.get(key, 0)
    
    # TODO: GENERATE VIOLENT ACTIONS
    res['violent_actions'] = 1337
    #modify name values
    res['non_uniformed'] = res.pop('Civilian')
    res['uniformed'] = res.pop('Officer')
    res['chemical_smoke'] = res.pop('Chemical Smoke')
    res['riot_shield'] = res.pop('Riot Shield')
    res['baton'] = res.pop('Baton')

    print(res)
    with open(f"temp_videodata_storage/{video_id}_stats.json", "w") as outfile:
        json.dump(res, outfile)
