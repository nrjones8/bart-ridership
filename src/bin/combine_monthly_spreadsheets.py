import calendar
import csv
import pandas as pd
import string

MONTH_NUM_FIELD = 'month_number'
YEAR_FIELD = 'year'
# e.g. 'weekday', 'saturday', etc.
PART_OF_WEEK_FIELD = 'part_of_week'
START_FIELD = 'start_station'
DEST_FIELD = 'dest_station'
AVG_NUM_RIDERS_FIELD = 'avg_num_riders'

COMBINED_DATA_COLS = [
    YEAR_FIELD, MONTH_NUM_FIELD, PART_OF_WEEK_FIELD, START_FIELD, DEST_FIELD, AVG_NUM_RIDERS_FIELD
]

FILES_FROM_2018_TO_SHEET_NAME = {
    # One of the 2018 "weekday" sheet names is different :`-(
    'Ridership_201801.xlsx': 'Weekday OD',
    'Ridership_201802.xlsx': 'Avg Weekday OD',
    'Ridership_201803.xlsx': 'Avg Weekday OD',
    'Ridership_201804.xlsx': 'Avg Weekday OD',
    'Ridership_201805.xlsx': 'Avg Weekday OD',
}

def get_station_names_map():
    stations_df = pd.read_csv('data/Station_Names.csv')
    code_to_name = {row['station_code']: row['station_name'] for index, row in stations_df.iterrows()}

    return code_to_name


def parse_ridership_spreadsheet(year, month_num, part_of_week, spreadsheet_path, sheet_name):
    """
    """
    spreadsheet = pd.read_excel(
        spreadsheet_path, sheet_name=sheet_name, header=1
    )
    station_names_map = get_station_names_map()
    station_codes = set(station_names_map.keys())

    ridership_data = []

    for exit_station, row in spreadsheet.iterrows():
        if str(exit_station) not in station_codes:
            # Some of the rows in the spreadsheet are aggregate data, e.g. the total number of
            # entrances at a given station. We don't want to parse that here, so make sure that
            # the `exit_station` is in fact a station.
            print 'Skipping row, not an actual station: "{}"'.format(exit_station)
            continue

        for enter_station in station_codes:
            # pandas sees `24`, and parses it to an int. Our station names are all strings, so
            # convert it to an int here to make sure we actually find the data in the `row`
            station_key = int(enter_station) if enter_station.isdigit() else enter_station
            # station_key = enter_station
            ridership_data.append({
                YEAR_FIELD: year,
                MONTH_NUM_FIELD: month_num,
                PART_OF_WEEK_FIELD: part_of_week,
                START_FIELD: str(enter_station),
                DEST_FIELD: str(exit_station),
                AVG_NUM_RIDERS_FIELD: row[station_key]
            })

    return pd.DataFrame(ridership_data)

def process_2017_data():
    """
    The naming of 2017 data files is slightly different than 2018, so just handle different years in
    different functions.
    """
    all_2017_data = pd.DataFrame(columns=COMBINED_DATA_COLS)

    sheet_name = 'Weekday OD'
    year = '2017'

    for month_num, month_name in enumerate(calendar.month_name):
        # This is ugly, I know
        if month_num == 0:
            continue
        full_file_name = 'data/raw/Ridership_{}2017.xlsx'.format(month_name)
        zero_padded_month_num = string.zfill(month_num, 2)

        one_month = parse_ridership_spreadsheet(
            year, zero_padded_month_num, 'weekday', full_file_name, sheet_name
        )
        all_2017_data = all_2017_data.append(one_month, ignore_index=True)

    return all_2017_data


def process_2018_data():
    all_2018_data = pd.DataFrame(columns=COMBINED_DATA_COLS)

    year = '2018'
    for month in ['01', '02', '03', '04', '05']:
        for part_of_week in ['weekday']:
            file_name = 'Ridership_{}{}.xlsx'.format(year, month)
            sheet_name = FILES_FROM_2018_TO_SHEET_NAME[file_name]

            full_file_name = 'data/raw/{}'.format(file_name)
            one_month = parse_ridership_spreadsheet(
                year, month, part_of_week, full_file_name, sheet_name
            )
            all_2018_data = all_2018_data.append(one_month, ignore_index=True)

    return all_2018_data

def check_value(df, year, month, start_station, dest_station, expected_num_riders):
    actual_num_riders = df[
        (df['year'] == year) &
        (df['month_number'] == month) &
        (df['start_station'] == start_station) &
        (df['dest_station'] == dest_station)
    ]['avg_num_riders'].round(0).item()

    if actual_num_riders != expected_num_riders:
        raise Exception(
            'Expected {}, but got {} for {}, {}, stations {} -> {}'.format(
                expected_num_riders,
                actual_num_riders,
                year,
                month,
                start_station,
                dest_station
            )
        )


def check_written_file(written_file_path):
    """
    Check a few specific entries in the written CSV to make sure we processed them correctly. The
    ridership numbers we're checking against were looked up by hand.
    """
    df = pd.read_csv(written_file_path)
    check_value(df, 2017, 3, 'CC', '24', 1087)
    check_value(df, 2018, 3, 'CC', '24', 999)

    check_value(df, 2017, 3, 'OR', 'EM', 927)
    check_value(df, 2018, 3, 'OR', 'EM', 896)

    check_value(df, 2017, 4, 'LF', 'MT', 703)
    check_value(df, 2018, 4, 'LF', 'MT', 721)
    print 'Checked a number of values in output file at "{}" - looks good'.format(written_file_path)


def write_2017_and_2018_weekday_data(out_path='data/2017_2018_weekday_data.csv'):
    data_from_2017 = process_2017_data()
    data_from_2018 = process_2018_data()

    combined_data = pd.concat([data_from_2017, data_from_2018])
    combined_data.to_csv(out_path, columns=COMBINED_DATA_COLS, index=False)
    print 'Wrote output to {}'.format(out_path)
    check_written_file(out_path)

if __name__ == '__main__':
    write_2017_and_2018_weekday_data()
