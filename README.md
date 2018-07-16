## Raw BART data
Data (in `.xlsx` format) comes from https://www.bart.gov/about/reports/ridership and is stored in this repo (at `data/raw/`). Each spreadsheet from BART provides data on monthly ridership between any 2 stations (e.g. "an average of 1900 people rode from Powell to 24th St on weekdays in June of 2018").

## To combine the spreadsheets provided by BART
To produce one unified `.csv` (which includes all data from 2017 and 2018), run:
```
python src/bin/combine_monthly_spreadsheets.py
```
which will update `data/2017_2018_weekday_data.csv` in this repo.