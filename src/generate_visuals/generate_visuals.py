import json
from time import time
import pandas as pd
import datetime as dt
import altair as alt

def generate_visuals(video_id, dev_mode=False):

    def sec_to_datetime(sec):
            import datetime

            convert = str(datetime.timedelta(seconds= sec))
            return convert  



    def format_and_export_plotly_to_json(chart):
        export_json_name = f'temp_videodata_storage/{video_id}_chart.json'
        (chart).save(export_json_name)

        with open(export_json_name) as f:
            data = json.load(f)
        
        
        # make edits to final visual json
        # append time list to end of data list
        #data['duration'] = data['datasets'][list(data['datasets'].keys())[0]][-1]['Seconds']
        
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
        
        correct_class_order = ['SECONDS', 'UNIFORMED PERSON', 'NON-UNIFORMED PERSON', 'CROWD','PERSON ON GROUND', 'RESTRAINING', 
                                'RUNNING', 'BRAWLING', 'SPRAY', 'STRIKING', 'THROWING', 'GUN', 'BATON', 'CHEMICAL SMOKE', 'RIOT SHIELD', 'PEPPER SPRAY']

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

        #TODO: THIS CODE IS WEAKSAUCE
        try:
            df = df.rename(columns={"Non Uniformed": "Non-Uniformed Person"})
        except:
            pass
        try:
            df = df.rename(columns={"Uniformed": "Uniformed Person"})
        except:
            pass

        df2 = df * -1
        df2['Seconds'] = df['Seconds'] * 1
        df = df.append(df2)
        df.sort_index()
        df.columns = df.columns.str.upper()
        # reorder df to correct class order

        final_list = []
        for val in correct_class_order:
            if val not in list(df.columns):
                pass
            else:
                final_list.append(val)

        #convert seconds to datetime
        
        #print("HERE", final_list, list(df.columns), correct_class_order)
        df = df[final_list]
        
        df['SECONDS'] = df['SECONDS'].apply(sec_to_datetime)
        df['SECONDS'] = pd.to_datetime(df['SECONDS'])
        return df


    color_map = {'BRAWLING':'#F2191A', 'RESTRAINING':'#F2191A', 'STRIKING':'#F2191A','THROWING': '#F2191A', 'RUNNING':'#F6AA28', 'CHEMICAL SMOKE':'#30B695', 'CROWD':'#F6AA28',
       'BATON':'#30B695', 'RIOT SHIELD':'#30B695', 'NON-UNIFORMED PERSON':'#4218D9', 'UNIFORMED PERSON':'#4218D9',
       'PERSON ON GROUND':'#F6AA28', 'SPRAY':'#F2191A', 'GUN':'#F2191A', 'PEPPER SPRAY':'#30B695'}

    df = create_df_all_models()

    # calculate bin
    vid_length_sec = len(df) / 2
    if vid_length_sec <= 120:
        bin_size = vid_length_sec * 3
    else:
        bin_size = 240
    
    interval = alt.selection(type='interval', encodings=['x'])

    base = alt.Chart(df).properties(    
        width='container',
        height=50,
    )

    chart = alt.vconcat(
        data=df,
        spacing=0,)

    for index, y_encoding in enumerate(list(df.columns[1:])):
        orient = 'bottom'
        ticks=False
        labels=False
        bar_color = color_map[y_encoding]

        if index == 0:
            labels = True
            orient = 'top'
            ticks = True
        if index == len(df.columns[1:]) - 1:
            ticks=True
            labels=True

        row = base.mark_bar().encode(
            alt.X('hoursminutesseconds(SECONDS):T', scale=alt.Scale(domain=interval),axis=alt.Axis(tickCount=10,labels=labels, title=None, ticks=ticks, orient=orient),
            ),
            alt.Y(y_encoding, axis=alt.Axis(titleAngle=0, titlePadding=80, labels=False, ticks=False)
            ),
            color=alt.value(bar_color),
            tooltip=[alt.Tooltip(y_encoding, title=f'{y_encoding.title()}'), alt.Tooltip('hoursminutesseconds(SECONDS):T', title='Timestamp')]
            ).properties(
                #width=1920
            )
        chart &= row

    view = base.mark_bar(size=2).encode(
        alt.X('hoursminutesseconds(SECONDS):T', title='Click and drag above to zoom', axis=alt.Axis(tickCount=10, orient='bottom')
        ),
    ).add_selection(
        interval
    )

    both = alt.VConcatChart(
        vconcat=[view, chart],
        spacing=50,
        padding={"left": 10, "top": 20, "right": 50, "bottom": 50},
        
    ).configure_axis(
        gridDash=[1,1],
        grid=True,
    )

    return format_and_export_plotly_to_json(both)

