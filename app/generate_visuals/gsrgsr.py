# matplotlib

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import json
import pandas as pd


# select json to generate data from
data = "test_combined.json"

def create_df_all_models(data):

    with open(data) as f:
        data = json.load(f)
    
    #f = open("demofile.txt", "r")
    # generate variables to be added to the df
    vidlength = data['videoInfo']['videoLength']
    unique_keys = set([_key for key,val in data['seconds'].items() for _key, _val in val.items()])
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

    # rename columns and clean names
    df.columns = map(str.title, df.columns)
    df.columns = df.columns.str.replace("_", " ")
    df = df.rename(columns={"Officer": "Uniformed Person", "Civilian": "Non-Uniformed Person"})
    # reorder columns
    #df = df[['seconds', 'Officer', 'Civilian', 'Chemical Smoke', 'Riot Shield', 'Baton', '']]
    print(df.columns)
    return df

df = create_df_all_models(data)

color_map = {'Brawling':'red', 'Restraining':'red', 'Striking':'red','Throwing': 'red', 'Brawling':'red', 'Running':'yellow', 'Chemical Smoke':'green', 'Crowd':'yellow',
       'Baton':'green', 'Riot Shield':'green', 'Non-Uniformed Person':'purple', 'Uniformed Person':'purple',
       'Person On Ground':'yellow', 'Spray':'red', 'Gun':'red', 'Pepper Spray':'green'}



df_col_names = list(df.columns[1:])

fig, axs = plt.subplots(len(df.columns)- 1, 1, figsize=(25,10))

def draw_graph():
    for ind, ax in enumerate(axs):
        #color
        col_name = df.columns[ind + 1]


        ax.hist(x=df['Seconds'],bins=200, weights=df[df_col_names[ind]], color=color_map[col_name])
        ax.hist(x=df['Seconds'],bins=200, weights=df[df_col_names[ind]] * -1, color=color_map[col_name])
        ax.set_ylabel(df_col_names[ind], rotation=0, ha='right')

        ax.margins(x=0)
        ax.axes.yaxis.set_ticklabels([])
        ax.axes.yaxis.set_ticks([])
        if ind == 0:
            ax.xaxis.tick_top()
        else:
            ax.axes.xaxis.set_ticklabels([])

plt.subplots_adjust(wspace=0, hspace=0)

draw_graph()


# SLIDER
ax_slide=plt.axes([.25,.1,.65,.03])
s_factor=Slider(ax_slide,"changing value",valmin=0,valmax=1.0,valinit=.5,valstep=0.01)

def update(val):
    plt.show()
    pass
 
s_factor.on_changed(update)

#plt.show()