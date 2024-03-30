import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gspread
import config

def getGames():
    url = f'https://docs.google.com/spreadsheets/d/{config.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={config.SHEET_NAME}'
    url = url.replace(" ", "%20")
    df = pd.read_csv(url)


    df1 = df.iloc[:, 0:131]
    df = df.reset_index()


    column_names = ['index','Date','Visitor','GP','CF','CA','CF%','FF','FA','FF%','SF','SA','SF%','GF','GA',
                    'GF%','xGF','xGA','xGF%','SCF','SCA','SCF%','SCSF','SCSA','SCSF%','SCGF','SCGA',
                    'SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%','HDSF','HDSA','HDSF%','HDGF','HDGA',
                    'HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%','MDSF','MDSA','MDSF%','MDGF','MDGA',
                    'MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%','LDSF','LDSA','LDSF%','LDGF','LDGA',
                    'LDGF%','LDSH%','LDSV%','SH%','SV%','PDO','Home','GP','CF','CA','CF%',
                    'FF','FA','FF%','SF','SA','SF%','GF','GA','GF%','xGF','xGA','xGF%','SCF','SCA','SCF%',
                    'SCSF','SCSA','SCSF%','SCGF','SCGA','SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%',
                    'HDSF','HDSA','HDSF%','HDGF','HDGA','HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%',
                    'MDSF','MDSA','MDSF%','MDGF','MDGA','MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%',
                    'LDSF','LDSA','LDSF%','LDGF','LDGA','LDGF%','LDSH%','LDSV%','SH%','SV%','PDO', 'Winner']
    df.columns = column_names
    df = df.drop('index', axis=1)

    
    return df

def get_stats():
    game_results = getGames()

    today = (datetime.today().date())

    url_template = "https://www.naturalstattrick.com/teamtable.php?fromseason=20232024&thruseason=20232024&stype=2&sit=5v5&score=all&rate=n&team=all&loc=B&gpf=410&fd=&td={}"


    formatted_date_url = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    url = url_template.format(formatted_date_url)

    formatted_date_current = today.strftime('%B %#d, %Y')

    current_day_games = game_results[game_results['Date'] == formatted_date_current]

    visitor_results = current_day_games.iloc[:, 0:65]
    visitor_results = visitor_results.rename(columns={"Visitor": "Team"})
    visitor_results = visitor_results.drop(["Date"], axis=1)

    home_results = current_day_games.iloc[:, 65:131]
    home_results = home_results.rename(columns={"Home": "Team"})
    home_results = home_results.drop(["Winner"], axis=1)

    current_day_stats = pd.read_html(url)
    current_day_stats = pd.DataFrame(current_day_stats[0])
    current_day_stats = current_day_stats.loc[:, ~current_day_stats.columns.str.contains('^Unnamed')]
    current_day_stats = current_day_stats.drop(["TOI","W","L","OTL","ROW","Points","Point %"], axis=1)

    for column in current_day_stats.columns:
        if current_day_stats[column].dtype == 'int64':
            current_day_stats[column] = current_day_stats[column].astype(np.float64)

    visitor_results = visitor_results.merge(current_day_stats, on='Team', how='left')
    visitor_results = visitor_results.drop(visitor_results.iloc[:, 1:64], axis=1)

    home_results = home_results.merge(current_day_stats, on='Team', how='left')
    home_results = home_results.drop(home_results.iloc[:, 1:64], axis=1)

    vcolumn_names = ['Visitor','GP','CF','CA','CF%','FF','FA','FF%','SF','SA','SF%','GF','GA',
                'GF%','xGF','xGA','xGF%','SCF','SCA','SCF%','SCSF','SCSA','SCSF%','SCGF','SCGA',
                'SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%','HDSF','HDSA','HDSF%','HDGF','HDGA',
                'HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%','MDSF','MDSA','MDSF%','MDGF','MDGA',
                'MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%','LDSF','LDSA','LDSF%','LDGF','LDGA',
                'LDGF%','LDSH%','LDSV%','SH%','SV%','PDO']
    hcolumn_names = ['Home','GP','CF','CA','CF%','FF','FA','FF%','SF','SA','SF%','GF','GA',
                'GF%','xGF','xGA','xGF%','SCF','SCA','SCF%','SCSF','SCSA','SCSF%','SCGF','SCGA',
                'SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%','HDSF','HDSA','HDSF%','HDGF','HDGA',
                'HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%','MDSF','MDSA','MDSF%','MDGF','MDGA',
                'MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%','LDSF','LDSA','LDSF%','LDGF','LDGA',
                'LDGF%','LDSH%','LDSV%','SH%','SV%','PDO']
    
    visitor_results.columns = vcolumn_names
    home_results.columns = hcolumn_names
     
    return visitor_results, home_results

def update_sheet(away_table,home_table, away_column, home_column, end_away, end_home):
    gc = gspread.service_account(filename=config.api_key)

    sh = gc.open_by_key(config.SHEET_ID)

    away_values_list = sh.sheet1.col_values(excel_column_to_number(away_column))

    home_values_list = sh.sheet1.col_values(excel_column_to_number(home_column))

    sh.sheet1.batch_update([{
        'range': away_column+str(len(away_values_list) + 1),
        'values': away_table,
    },
    {
        'range': home_column+str(len(home_values_list) + 1),
        'values': home_table
    }])

    away_range = away_column + str(len(away_values_list) + 1) + ':' + end_away + str(len(away_values_list) + len(away_table))
    home_range = home_column + str(len(home_values_list) + 1) + ':' + end_home + str(len(home_values_list) + len(home_table))

    sh.sheet1.batch_format([{
        "range": away_range,
        "format":{
            "horizontalAlignment": 'CENTER'
        }
    },
    {
        "range": home_range,
        "format":{
            "horizontalAlignment": 'CENTER'
        }
    }])

def excel_column_to_number(column):
    column = column.upper()
    column_number = 0
    for char in column:
        column_number = column_number * 26 + (ord(char) - ord('A')) + 1
    return column_number

def main():
    away, home = get_stats()

    away = away.drop(["Visitor"], axis=1)
    away = away.values.tolist()

    home = home.drop(["Home"], axis=1)
    home = home.values.tolist()

    update_sheet(away, home, 'C', 'BO', 'BM', 'DY')

if __name__ == "__main__":
    main()