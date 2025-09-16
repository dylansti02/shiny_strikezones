import pybaseball as pb
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as ss
import matplotlib.ticker 

def get_league_average(stat: str, start_dt: str, end_dt: str):
    league_avgs = {
        'xwOBA': {
            '2015': 0.309, '2016': 0.315, '2017': 0.318, '2018': 0.313,
            '2019': 0.319, '2020': 0.323, '2021': 0.316, '2022': 0.309,
            '2023': 0.320, '2024': 0.312
        },
        'xSLG': {
            '2015': 0.390, '2016': 0.406, '2017': 0.415, '2018': 0.399,
            '2019': 0.424, '2020': 0.415, '2021': 0.407, '2022': 0.388,
            '2023': 0.412, '2024': 0.397
        },
        'xBA': {
            '2015': 0.245, '2016': 0.248, '2017': 0.249, '2018': 0.242,
            '2019': 0.246, '2020': 0.244, '2021': 0.242, '2022': 0.240,
            '2023': 0.248, '2024': 0.243
        },
        'wOBA': {
            '2015': 0.313, '2016': 0.318, '2017': 0.321, '2018': 0.315,
            '2019': 0.320, '2020': 0.320, '2021': 0.314, '2022': 0.310,
            '2023': 0.318, '2024': 0.310
        }}
    year_range = pd.date_range(start=start_dt, end=end_dt).year.unique()
    if len(year_range) == 1:
        yr = str(year_range[0])
        if yr in league_avgs[stat]:
            return league_avgs[stat][yr]
        elif yr == '2025':
            print(" Using 2024 average as placeholder for 2025.")
            return league_avgs[stat]['2024']

    known_years = [str(y) for y in year_range if str(y) in league_avgs[stat]]
    avg_values = [league_avgs[stat][y] for y in known_years]
    if 2025 in year_range:
        print("Using 2024 as placeholder for 2025 in multi-year average.")
        avg_values.append(league_avgs[stat]['2024'])

    if avg_values:
        return sum(avg_values) / len(avg_values)


pitch_family_map = {
    # Fastballs
    'FF': 'Fastball', 'FT': 'Fastball', 'SI': 'Fastball', 'FC': 'Fastball', 'FA': 'Fastball',
    
    # Breaking Balls
    'SL': 'Breaking', 'CU': 'Breaking', 'KC': 'Breaking', 'SV': 'Breaking', 'KN': 'Breaking', 'SC': 'Breaking', 'CS': 'Breaking',
    
    # Offspeed
    'CH': 'Offspeed', 'FS': 'Offspeed', 'FO': 'Offspeed', 'EP': 'Offspeed'
}