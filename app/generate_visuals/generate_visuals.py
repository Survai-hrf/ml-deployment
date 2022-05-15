from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import pandas as pd
import datetime as dt
import plotly


def generate_visuals(combined_json, video_id):
    
    data = combined_json

    def create_df_all_models(data):

        with open(data) as f:
            data = json.load(f)
        
        #f = open("demofile.txt", "r")
        # generate variables to be added to the df
        vidlength = data['videoInfo']['videoLength']
        unique_keys = set([_key for key,val in data['seconds'].items() for _key, _val in val.items()])
        print(unique_keys)
        df = pd.DataFrame({'seconds': range(0, vidlength +1)})
        df['seconds'] = pd.to_datetime(df["seconds"], unit='s').dt.strftime('%H:%M:%S')

        #add placeholder values
        for unique_key in unique_keys:
            df[unique_key] = 0

        #impute real values in their corresponding seconds
        for second, vals in data['seconds'].items():
            for _key, _val in vals.items():

                df.at[int(second), _key] = _val
        df['seconds'] = pd.to_datetime(df['seconds'])
        # reorder columns
        #df = df[['seconds', 'Officer', 'Civilian', 'Chemical Smoke', 'Riot Shield', 'Baton', '']]
        return df



    df = create_df_all_models(data)


    def format_and_export_plotly_to_json(fig, data):

        file_name_split = data.split('.')[0]
        export_json_name = f'{file_name_split}_plotly.json'
        plotly.io.write_json(fig, export_json_name, validate=True, pretty=False, remove_uids=True)

        with open(export_json_name) as f:
            data = json.load(f)

        time_list = df['seconds'].to_list()

        # ALWAYS append time list to end of data list
        data['data'].append({'duration': time_list})
        data
        for i in data['data']:
            
            # if i['x'] exists
            try:
                del i['x']
            except:
                continue
        
        with open(export_json_name, "w") as outfile:
            json.dump(data, outfile)



    # fig 2 with histogram
    #keep track of detection colors
    bins = 400

    #detection_colors = {'Officer': 'blue', 'Civilian': 'blue', 'Baton': 'green', 'Gun':'green', 'Riot Shield': 'green', 'Chemical Smoke': 'red', 'Pepper Spray': 'red'}

    x = df['seconds']
    y = df['Officer']

    fig = make_subplots(
        rows=len(df.columns)-1, 
        cols=1,
        shared_xaxes=True,
        subplot_titles=df.columns[1:],
        vertical_spacing=0,
        column_widths=[1],
        
        )

    # add the bars into the graph
    for i, val in enumerate(df.columns):
        if val == 'seconds':
            continue
        fig.add_trace(
            go.Histogram(
            x=df['seconds'],
            y=df[val],
            histfunc='sum',
            #marker=dict(color=detection_colors[val]),
            nbinsx=bins
        ),row=i, col=1),
        # add negative of same values to flip the bars on the same graph
        fig.add_trace(
            go.Histogram(
            x=df['seconds'],
            y=df[val] * -1,
            histfunc='sum',
            nbinsx=bins,
            #marker=dict(color=detection_colors[val]),
            
        ),row=i, col=1)

    fig.update_layout(
        showlegend=False,
        height = 400,
        width = 1500,
        barmode='overlay',
        margin=dict(
        l=150,
        r=10,
        b=20,
        t=30,
        pad=0
        ),
        )

    for i in range(1, len(df.columns)):
        fig.update_yaxes(
        row=i, col=1, side='left', showticklabels=False, showgrid=False, linewidth=1, linecolor='black', mirror=True,)

        if i == 1:
            fig.update_xaxes(row=i, col=1, side='top',linewidth=1, linecolor='gray', mirror=True,nticks=12)
        else:
            fig.update_xaxes(row=i, col=1, showticklabels=False, linewidth=1, linecolor='gray', mirror=True)

    for i in range(0, len(df.columns[1:])):
        fig.layout.annotations[i].update(x=-0.06)
        fig.layout.annotations[i]['y'] = fig.layout.annotations[i]['y'] - 0.11

    fig.show()
    print(data)

    return {}

generate_visuals("../temp_videodata_storage/test_combined.json", 1)