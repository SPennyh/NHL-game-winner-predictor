import pandas as pd
import numpy as np
from datetime import datetime
import gspread
import config

def get_todays_winner(today):
    data = pd.read_html("https://www.naturalstattrick.com/games.php")
    abbreviations = pd.read_csv("Abbreviations.csv")

    data = pd.DataFrame(data[0])
    data = data.iloc[::2]
    games = data['Game'].str.split(", ", expand=True)
    games = pd.DataFrame(games)

    date = games[0].str.split("- ", expand=True)
    away = date[1]
    date = date[0]
    home = games[1]

    home_score = home.str.rsplit(" ", n = 1, expand=True)
    home_team = home_score[0]
    home_score = home_score[1]

    away_score = away.str.rsplit(" ", n = 1, expand=True)
    away_team = away_score[0]
    away_score = away_score[1]

    games = pd.DataFrame(data = {"Date": date, 
                                 "Away Team": away_team.values, 
                                 "Away Score": away_score, 
                                 "Home Team": home_team, 
                                 "Home Score": home_score})
    games['Winner'] = np.where(games['Away Score'] > games['Home Score'], games['Away Team'],
                                np.where(games['Away Score'] < games['Home Score'], games['Home Team'], 0))
    games['Date'] = pd.to_datetime(games['Date'])

    abrev = pd.Series(abbreviations.Team.values, index=abbreviations.name).to_dict()
    games["Away Team"] = games['Away Team'].replace(abrev)
    games["Home Team"] = games['Home Team'].replace(abrev)
    games["Winner"] = games['Winner'].replace(abrev)

    formatted_date_current = today.strftime('%B %#d, %Y')

    winner = games[games['Date'] == formatted_date_current]
    away_t = winner['Away Team']
    home_t = winner['Home Team']
    temp = pd.DataFrame({'Away Team': away_t, 'Home Team': home_t})

    return winner['Winner']

def excel_column_to_number(column):
    column = column.upper()
    column_number = 0
    for char in column:
        column_number = column_number * 26 + (ord(char) - ord('A')) + 1
    return column_number

def update_sheet(table, column, worksheet_name):
    gc = gspread.service_account(filename=config.api_key)
    sh = gc.open_by_key(config.SHEET_ID)
    sheet = sh.worksheet(worksheet_name)

    values_list = sheet.col_values(excel_column_to_number(column))

    sheet.batch_update([{
        'range': column+str(len(values_list) + 1),
        'values': [table],
        'majorDimension': 'COLUMNS'
    }])

def update_success(column, size, worksheet_name):
    gc = gspread.service_account(filename=config.api_key)
    sh = gc.open_by_key(config.SHEET_ID)
    sheet = sh.worksheet(worksheet_name)

    values_list = sheet.col_values(excel_column_to_number(column))
    form = "=IF((D{}=E{}), 1, 0)"

    formulas = []
    for i in range(size):
        formulas.append(form.format(len(values_list) + i + 1, len(values_list) + i + 1))

    update_data = [{'range': column + str(len(values_list) + i + 1),
                    'values': [[formulas[i]]]} for i in range(size)]

    for data in update_data:
        sheet.update(data['range'], data['values'], value_input_option='USER_ENTERED')


def main():
    today = (datetime.today().date())
    winners = get_todays_winner(today)

    winners = winners.values.tolist()

    update_sheet(winners, 'DZ', "Advanced Stats")
    update_sheet(winners, 'E', "Results")
    update_success('F', len(winners), "Results")

if __name__ == "__main__":
    main()