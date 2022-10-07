import json



def generate_master(video_id):

    with open(f"temp_videodata_storage/{video_id}_stats.json") as f:
        stats = json.load(f)
    with open(f"temp_videodata_storage/{video_id}_chart.json") as f:
        visual = json.load(f)
        
    stats['chart'] = visual
    stats['uniqueID'] = video_id

    return stats

