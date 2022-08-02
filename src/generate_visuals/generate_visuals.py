
import json
import pandas as pd
import datetime as dt
import altair as alt

def generate_visuals(video_id, dev_mode=False):

    def format_and_export_plotly_to_json(view, chart):
        export_json_name = f'temp_videodata_storage/{video_id}_chart.json'
        (view & chart).save(export_json_name)

        with open(export_json_name) as f:
            data = json.load(f)
        
        # make edits to final visual json
        # append time list to end of data list
        data['duration'] = data['datasets'][list(data['datasets'].keys())[0]][-1]['Seconds']
        
        with open(export_json_name, "w") as outfile:
            json.dump(data, outfile)
        
        """
        doesn't work with altair_saver. needs conda-forge install, which was upgrading pytorch
        if dev_mode == True:
            (view & chart).save(f"temp_videodata_storage/{video_id}_chartviz.png")"""


    def create_df_all_models():
        '''creates formatted df from combined model data, and returns two dfs, one reversed'''

        with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
            data = json.load(f)
        
        # generate variables to be added to the df
        vidlength = data['videoInfo']['videoLength']
        unique_keys = set([_key for key,val in data['seconds'].items() for _key, _val in val.items()])
        df = pd.DataFrame({'seconds': range(0, vidlength +1)})
        #df['seconds'] = pd.to_datetime(df["seconds"], unit='s').dt.strftime('%H:%M:%S')

        #add placeholder values
        for unique_key in unique_keys:
            df[unique_key] = 0
        
        #impute real values in their corresponding seconds
        for second, vals in data['seconds'].items():
            for _key, _val in vals.items():
                df.at[int(second), _key] = _val

        #df['seconds'] = pd.to_datetime(df['seconds'])
        
        # rename columns and clean names
        df.columns = map(str.title, df.columns)
        df.columns = df.columns.str.replace("_", " ")
        df = df.rename(columns={"Officer": "Uniformed Person", "Civilian": "Non-Uniformed Person"})

        df2 = df * -1
        df2['Seconds'] = df['Seconds'] * 1
        df = df.append(df2)
        df.sort_index()
        return df


    df = create_df_all_models()

    #print csv of all detections if dev mode specified
    if dev_mode == True:
        df.to_csv(f'processed/detect_{video_id}.csv')


    #generate graph
    interval = alt.selection_interval(encodings=['x'])

    base = alt.Chart(df).properties(    
        width=1500,
        height=50,
    )

    chart = base.mark_bar().encode(
        alt.X('Seconds', bin=alt.Bin(maxbins=150, extent=interval), scale=alt.Scale(domain=interval.ref())),
        alt.Y(alt.repeat('row'), type='quantitative'),
    ).repeat(
        row=list(df.columns)[1:],
    )

    view = base.mark_bar().encode(
        alt.X('Seconds', title='click and drag and use mousewheel above to zoom'),
    ).add_selection(
        interval
    ).properties(
        height=100
    )

    return format_and_export_plotly_to_json(view, chart)

