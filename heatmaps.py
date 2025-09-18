import pybaseball as pb
pb.cache.enable()
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as ss
import matplotlib.ticker 

from helpers import get_league_average, pitch_family_map


def statcast_heatmap(player:  str=None, start_dt = '2015-01-01', end_dt=None, p_throws = None, pitch_type:  str = None):
        
        name_parts = player.split(" ")  
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])  


        player_info = pb.playerid_lookup(last_name, first_name)
        player_id = player_info.iloc[0]["key_mlbam"]


        if end_dt == None:
            from datetime import date
            end_dt = date.today().strftime('%Y-%m-%d')

        if pd.date_range(start_dt, end_dt).year.unique().min()<2015:
            raise ValueError('No Statcast data available before 2015.  Use start_dt = 2015-01-01 or later')

        #collect data, convert to inches, remove ST games and other NANs    
        df_test = pb.statcast_batter(player_id=player_id, start_dt=start_dt, end_dt=end_dt)
        df_test = df_test[df_test['game_type']!= 'S']
        df_test = df_test.dropna(subset=['plate_x', 'plate_z', 'sz_top', 'sz_bot'])

        if pitch_type is not None:

            pitch_type_lower = pitch_type.lower()

            if pitch_type_lower not in ['fastball', 'breaking', 'offspeed']:
                 raise ValueError('Please pass one of the following pitch types:  fastball, breaking, offspeed.  You can also leave blank for all pitches')

            df_test['pitch_family'] = df_test['pitch_type'].map(pitch_family_map)
            
            df_test['pitch_family'] = df_test['pitch_family'].str.lower()
    
            df_test = df_test[df_test['pitch_family'] == pitch_type_lower]


        if p_throws is not None:
            if p_throws not in ['l', 'L', 'left', 'Left', 'lefty', 'Lefty', 'r', 'R', 'right', 'Right', 'righty' ,'Righty' ]:
             raise ValueError("Please pass one of L or R to p_throws")
            elif p_throws in ['l', 'L', 'left', 'Left', 'lefty', 'Lefty']:
                df_test = df_test[df_test['p_throws']=='L']
            else:
                df_test = df_test[df_test['p_throws']=='R']    


        df_test['plate_x_in']=(df_test['plate_x']*12).round(2)
        df_test['plate_z_in']=(df_test['plate_z']*12).round(2)
        df_test['sz_bot_in']=(df_test['sz_bot']*12).round(2)
        df_test['sz_top_in']=(df_test['sz_top']*12).round(2)


        #define strike zone x-coords by middle 95% of called strikes in sample    
        strikes=df_test[df_test['description']=='called_strike']['plate_x_in'].sort_values()
        sz_left_in = np.nanpercentile(strikes.values, 2.5).round(2)
        sz_right_in = np.nanpercentile(strikes.values, 97.5).round(2)


        #define bins to plot 
        bin_width=((sz_right_in-sz_left_in).round(2))/3
        xmin=np.nanpercentile(df_test['plate_x_in'], 2.5)
        xmax=np.nanpercentile(df_test['plate_x_in'], 97.5)

        x_bins = pd.IntervalIndex.from_tuples([
            ((-0.01+xmin), sz_left_in-0.01), 
            (sz_left_in, sz_left_in+bin_width-0.01), 
            (sz_left_in+bin_width, sz_left_in+(2*bin_width)-0.01),
            (sz_left_in+(2*bin_width), sz_right_in-0.01),
            (sz_right_in, xmax+0.01)])


        #define strike zone z-coords by average of given strike zones
        sz_top_in = df_test['sz_top_in'].mean().round(2)
        sz_bot_in = df_test['sz_bot_in'].mean().round(2)

        bin_height = (((sz_top_in-sz_bot_in))/3).round(2)

        zmin=np.nanpercentile(df_test['plate_z_in'], 2.5)
        zmax=np.nanpercentile(df_test['plate_z_in'], 97.5)

        z_bins = pd.IntervalIndex.from_tuples([
            (zmin-0.01, sz_bot_in-0.01),
            (sz_bot_in, sz_bot_in+bin_height-0.01),
            (sz_bot_in+bin_height, sz_bot_in+(2*bin_height)-0.01),
            (sz_bot_in+(2*bin_height), sz_top_in+0.01),
            (sz_top_in+0.02, zmax)])
        
        #cut by bins
        df_test['plate_x_in_bin'] = pd.cut(df_test['plate_x_in'], bins=x_bins)
        df_test['plate_z_in_bin'] = pd.cut(df_test['plate_z_in'], bins=z_bins)
        df_test['plate_x_in_center'] = df_test['plate_x_in_bin'].apply(lambda x: x.mid if pd.notnull(x) else np.nan)
        df_test['plate_z_in_center'] = df_test['plate_z_in_bin'].apply(lambda x: x.mid if pd.notnull(x) else np.nan)

        #create plotting dfs by pivottable
        df_plot_slug = df_test.pivot_table(
            index='plate_z_in_center', 
            columns='plate_x_in_center', 
            values='estimated_slg_using_speedangle',
            aggfunc='mean')

        df_plot_slug=df_plot_slug.iloc[::-1]


        df_plot_slug = df_plot_slug.apply(pd.to_numeric, errors='coerce').astype(float)
        df_plot_slug = df_plot_slug.fillna(np.nan)

        df_plot_xwoba = df_test.pivot_table(
            index='plate_z_in_center', 
            columns='plate_x_in_center', 
            values='estimated_woba_using_speedangle',
            aggfunc='mean')

        df_plot_xwoba=df_plot_xwoba.iloc[::-1]


        df_plot_xwoba = df_plot_xwoba.apply(pd.to_numeric, errors='coerce').astype(float)
        df_plot_xwoba = df_plot_xwoba.fillna(np.nan)

        df_plot_woba = df_test.pivot_table(
            index='plate_z_in_center', 
            columns='plate_x_in_center', 
            values='woba_value',
            aggfunc='mean')

        df_plot_woba=df_plot_woba.iloc[::-1]


        df_plot_woba = df_plot_woba.apply(pd.to_numeric, errors='coerce').astype(float)
        df_plot_woba = df_plot_woba.fillna(np.nan)

        df_plot_xba = df_test.pivot_table(
            index='plate_z_in_center', 
            columns='plate_x_in_center', 
            values='estimated_ba_using_speedangle',
            aggfunc='mean')

        df_plot_xba=df_plot_xba.iloc[::-1]


        df_plot_xba = df_plot_xba.apply(pd.to_numeric, errors='coerce').astype(float)
        df_plot_xba = df_plot_xba.fillna(np.nan)


        #plot 
        # Dictionary of dataframes per metric
        metric_dfs = {
            'xwOBA': df_plot_xwoba,
            'xSLG': df_plot_slug,
            'xBA': df_plot_xba,
            'wOBA': df_plot_woba}

        # Corresponding column names for centering
        metric_statcast_columns = {
            'xwOBA': 'estimated_woba_using_speedangle',
            'xSLG': 'estimated_slg_using_speedangle',
            'xBA': 'estimated_ba_using_speedangle',
            'wOBA': 'woba_value'}

        # Set up 2x2 grid
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))  # Adjust size as needed
        axes = axes.flatten()  # Flatten 2D array to 1D list for easy indexing

        # Plot each metric on its corresponding axis
        for i, (metric, df_plot) in enumerate(metric_dfs.items()):
            ax = axes[i]
            sns.heatmap(
            df_plot,
            center=get_league_average(metric, start_dt, end_dt),
            cmap='coolwarm',
            annot=True,
            fmt='.3f',
            cbar=False,
            xticklabels=x_bins.mid,
            yticklabels=z_bins[::-1].mid,
            ax=ax)

            ax.set_title(f'{metric} by Pitch Location')
            ax.set_xlabel('Distance From Center of Strike Zone (in)')
            ax.set_ylabel('Height of Pitch (in)')
            ax.set_xticklabels([f"{v:.2f}" for v in x_bins.mid])
            ax.set_yticklabels([f"{v:.2f}" for v in z_bins[::-1].mid])

            # Strike zone box (same logic per subplot)
            ax.axhline(y=1, xmin=0.2, xmax=0.8)
            ax.axhline(y=4, xmin=0.2, xmax=0.8)
            ax.axvline(x=1, ymin=0.2, ymax=0.8)
            ax.axvline(x=4, ymin=0.2, ymax=0.8)

           

        #Add appropriate title

        title = f'Statcast Metrics for {player}'

        if p_throws is not None:
            handedness_map = {
        'l': 'Left-Handed Pitching', 'left': 'Left-Handed Pitching',
        'r': 'Right-Handed Pitching', 'right': 'Right-Handed Pitching', 
        'righty': 'Right-Handed Pitching', 'lefty':  'Left-Handed Pitching'}
            normalized_hand = p_throws.lower()
            if normalized_hand in handedness_map:
                title += f' vs {handedness_map[normalized_hand]}'
        if pitch_type is not None:
            title += f', {pitch_type_lower.capitalize()}'
        title += f' ({start_dt} to {end_dt})'
        fig.suptitle(title, fontsize=16)
        
        

    

        # Adjust layout and show plots
        plt.tight_layout() 
        return fig