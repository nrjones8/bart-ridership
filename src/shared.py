import pandas as pd

from pandas.api.types import CategoricalDtype

def prep_yoy_data():
    ridership_df = pd.read_csv('data/2017_2018_weekday_data.csv')
    stations_df = pd.read_csv('data/Station_Names.csv')
    stations_map = {row['station_code']: row['station_name'] for index, row in stations_df.iterrows()}


    # output should be
    # start_station | end_station | month | 2017_avg | 2018_avg | diff_in_avgs
    pivoted = ridership_df.pivot_table(
        values='avg_num_riders',
        index=['month_number', 'part_of_week', 'start_station', 'dest_station'],
        columns=['year']
    ).reset_index()

    # ugh, these should be strings
    pivoted['diff_2017_to_2018'] = pivoted[2018] - pivoted[2017]
    pivoted['diff_pct_2017_to_2018'] = pivoted[2018] / pivoted[2017]

    # Add full station names
    station_cat_type = CategoricalDtype(categories=stations_df['station_code'], ordered=True)
    pivoted['categorical_from_station'] = pivoted['start_station'].astype(station_cat_type)
    pivoted['categorical_dest_station'] = pivoted['dest_station'].astype(station_cat_type)

    pivoted['from_station_full'] = pivoted.apply(lambda row: stations_map[row['start_station']], axis=1)
    pivoted['to_station_full'] = pivoted.apply(lambda row: stations_map[row['dest_station']], axis=1)
    print pivoted.head()

    return pivoted