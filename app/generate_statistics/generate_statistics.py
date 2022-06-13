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

    with open(f"temp_videodata_storage/{video_id}_stats.json", "w") as outfile:
        json.dump(res, outfile)
