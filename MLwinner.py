import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from datetime import datetime, timedelta, date
import gspread
import config

def getGames():
    url = f'https://docs.google.com/spreadsheets/d/{config.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={config.SHEET_NAME}'
    url = url.replace(" ", "%20")
    df = pd.read_csv(url)

    df1 = df.iloc[:, 0:130]
    df = df1.drop([0,1])
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
                    'LDSF','LDSA','LDSF%','LDGF','LDGA','LDGF%','LDSH%','LDSV%','SH%','SV%','PDO','Winner']
    df.columns = column_names
    df = df.drop('index', axis=1)
    return df

def getTodayGames(df, day):
    today = df[df['Date'] == day]

    return today

def update_sheet(prediction, column, worksheet_name):
    gc = gspread.service_account(filename=config.api_key)

    sh = gc.open_by_key(config.SHEET_ID)

    sheet = sh.worksheet(worksheet_name)

    values_list = sheet.col_values(excel_column_to_number(column))

    sheet.batch_update([{
        'range': column+str(len(values_list) + 1),
        'values': [prediction],
        'majorDimension': 'COLUMNS'
    }])

def excel_column_to_number(column):
    column = column.upper()
    column_number = 0
    for char in column:
        column_number = column_number * 26 + (ord(char) - ord('A')) + 1
    return column_number

def random_forest_prediction(x_train, y_train, leafs):
    rf_model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=3000, min_samples_leaf=leafs, random_state=20, bootstrap=False, n_jobs=-1) #best 35
    )
    return rf_model.fit(x_train, y_train)

def mlp_prediction(x_train, y_train):
    mlp_model = make_pipeline(                                                          #multi-layer perceptron model
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(115,80,40), max_iter=300)
    )
    return mlp_model.fit(x_train, y_train)

def svc_prediction(x_train, y_train):
    svc_model = make_pipeline(                                                          #support vector classification model
        StandardScaler(),   
        SVC(kernel = 'linear', shrinking = False)
    )
    return svc_model.fit(x_train, y_train)


def main():
    game_results = getGames()

    today = (datetime.today().date()).strftime('%B %#d, %Y')

    temp_games = game_results
    game_results = game_results[game_results['Date'] != today]

    team_encoder = LabelEncoder()

    team_encoder.fit(game_results['Visitor'])
    game_results['Visistor_e'] = team_encoder.transform(game_results['Visitor'])
    game_results['Home_e'] = team_encoder.transform(game_results['Home'])
    game_results['Winner_e'] = team_encoder.transform(game_results['Winner'])

    X = game_results.drop(columns=['Date', 'Visitor', 'Home', 'Winner', 'Winner_e'])
    y = game_results['Winner_e']


    unlabelled = getTodayGames(temp_games, today)
    unlabelled['Visistor_e'] = team_encoder.transform(unlabelled['Visitor'])
    unlabelled['Home_e'] = team_encoder.transform(unlabelled['Home'])
    X_unlabelled = unlabelled.drop(columns=['Date', 'Visitor', 'Home', 'Winner'])

    some_value = 0
    if unlabelled.shape[0] <= 5:
        some_value = 4
    elif unlabelled.shape[0] > 5 and unlabelled.shape[0] <= 14:
        some_value = 6
    else:
        some_value = 7

    print(some_value)

    #Training random forest model 
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=some_value) #best 6, 52
    X_train.fillna(X_train.mean(), inplace = True)
    X_test.fillna(X_train.mean(), inplace = True)

    rf_model = random_forest_prediction(X_train, y_train, some_value)
    #mlp_model = mlp_prediction(X_train, y_train)
    #svc_model = svc_prediction(X_train, y_train)


    #scoring random forest model
    accuracy = rf_model.score(X_train, y_train)
    test_accuracy = rf_model.score(X_test, y_test)
    print(f'Train Accuracy: {accuracy}')
    print(f'Test Accuracy: {test_accuracy}')
    predictions = rf_model.predict(X_unlabelled)
    print(team_encoder.inverse_transform(predictions))
    pred = pd.Series(team_encoder.inverse_transform(predictions))
    pred = pred.values.tolist()
    update_sheet(pred, "D", "Results")


if __name__ == "__main__":
    main()