import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import gspread
import config

def get_games():
    data = pd.read_html("https://www.naturalstattrick.com/")

    count = 0
    away = np.empty(shape=len(data), dtype=object)
    home = np.empty(shape=len(data), dtype=object)
    for teams in data:
        matchups = teams[[0]]

        away[count] = matchups[0][0]
        home[count] = matchups[0][1]
        count += 1
    
    games = pd.DataFrame({'Away': away, 'Home': home})
    games['Date'] = (datetime.today().date()).strftime('%#m/%#d/%Y')

    return games

def fix_abrev(table):
    abbreviations = pd.read_csv("Abbreviations.csv")
    abrev = pd.Series(abbreviations.Team.values, index=abbreviations.name).to_dict()
    table["Away"] = table['Away'].replace(abrev)
    table["Home"] = table['Home'].replace(abrev)

    return table

def excel_column_to_number(column):
    column = column.upper()
    column_number = 0
    for char in column:
        column_number = column_number * 26 + (ord(char) - ord('A')) + 1
    return column_number


def update_sheet(away_table, home_table, date, away_column, home_column, date_column, worksheet_name):
    gc = gspread.service_account(filename=config.api_key)

    sh = gc.open_by_key(config.SHEET_ID)

    sheet = sh.worksheet(worksheet_name)

    values_list = sheet.col_values(excel_column_to_number(away_column))

    sheet.batch_update([{
        'range': away_column+str(len(values_list) + 1),
        'values': [away_table],
        'majorDimension': 'COLUMNS'
    },
    {
        'range': home_column+str(len(values_list) + 1),
        'values': [home_table],
        'majorDimension': 'COLUMNS'
    }])
    

    update_data = [{'range': date_column + str(len(values_list) + i + 1),
                    'values': [[date[i]]]} for i in range(len(date))]

    for data in update_data:
        sheet.update(range_name=data['range'], values=data['values'], value_input_option='USER_ENTERED')

    sheet.batch_format([{
        "range": date_column+str(len(values_list) + 1 )+':'+date_column+str(len(values_list) + len(date)),
        "format": {
            "numberFormat": {
                "type": "DATE",
                "pattern": "mmmm d, yyyy"
            },
            "horizontalAlignment": 'LEFT'
        }
    }])

    print(worksheet_name + " has been updated!")


        

def main():
    games = get_games()

    games = fix_abrev(games)

    update_sheet(games['Away'].values.tolist(), games['Home'].values.tolist(), games['Date'].values.tolist(), 'B', 'BN', 'A', "Advanced Stats")
    update_sheet(games['Away'].values.tolist(), games['Home'].values.tolist(), games['Date'].values.tolist(), 'B', 'C', 'A', "Results")

    
if __name__ == "__main__":
    main()
