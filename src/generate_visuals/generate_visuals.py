from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import pandas as pd
import datetime as dt
import plotly


def generate_visuals(video_id):

    def format_and_export_plotly_to_json(fig):

        export_json_name = f'temp_videodata_storage/{video_id}_plotly.json'
        plotly.io.write_json(fig, export_json_name, validate=True, pretty=False, remove_uids=True)

        with open(export_json_name) as f:
            data = json.load(f)
        
        # make edits to final visual json
        with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
            combined_data = json.load(f)

        #time_list = df['seconds'].to_list()
        # ALWAYS append time list to end of data list
        data['data'].append({'duration': combined_data['videoInfo']['videoLength']})
        
        with open(export_json_name, "w") as outfile:
            json.dump(data, outfile)



    def create_df_all_models():
        with open(f"temp_videodata_storage/{video_id}_combined.json") as f:
            data = json.load(f)


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
        # TODO: reorder columns to be in right order

        return df



    df = create_df_all_models()

    # create fig with histogram
    bins = 200
    #TODO: Generate appropriate colors
    #detection_colors = {'Officer': 'blue', 'Civilian': 'blue', 'Baton': 'green', 'Gun':'green', 'Riot Shield': 'green', 'Chemical Smoke': 'red', 'Pepper Spray': 'red'}

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
            marker=dict(color='blue'),
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
            marker=dict(color='blue')
            #marker=dict(color=detection_colors[val]),
            
        ),row=i, col=1)

    fig.update_layout(
        showlegend=False,
        height = 400,
        width = 1500,
        barmode='relative',
        bargap=0,
        bargroupgap=0,
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
            fig.update_xaxes(row=i, col=1, side='top',linewidth=1, linecolor='gray', mirror=True,showticklabels=True, nticks=12)
        else:
            fig.update_xaxes(row=i, col=1, showticklabels=False, linewidth=1, linecolor='gray', mirror=True)

    for i in range(0, len(df.columns[1:])):
        fig.layout.annotations[i].update(x=-0.06)
        fig.layout.annotations[i]['y'] = fig.layout.annotations[i]['y'] - 0.08



    return format_and_export_plotly_to_json(fig)

