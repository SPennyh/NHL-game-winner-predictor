import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.neural_network import MLPClassifier

def getGames():
    SHEET_ID = '1rjv6ncPJ7pHaxQGdiYbMHa1zOM3LvzcojBXzq8e6pdU'
    SHEET_NAME = 'Advanced Stats (per game avgs)'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    url = url.replace(" ", "%20")
    df = pd.read_csv(url)

    #df.columns = df.iloc[1]
    df1 = df.iloc[:, 0:134]
    df = df1.drop([0,1])
    df = df.reset_index()
    column_names = ['index','Date','Visitor','GP','CF','CA','CF%','FF','FA','FF%','SF','SA','SF%','GF','GA',
                    'GF%','xGF','xGA','xGF%','SCF','SCA','SCF%','SCSF','SCSA','SCSF%','SCGF','SCGA',
                    'SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%','HDSF','HDSA','HDSF%','HDGF','HDGA',
                    'HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%','MDSF','MDSA','MDSF%','MDGF','MDGA',
                    'MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%','LDSF','LDSA','LDSF%','LDGF','LDGA',
                    'LDGF%','LDSH%','LDSV%','SH%','SV%','PDO','ML','Units','Home','GP','CF','CA','CF%',
                    'FF','FA','FF%','SF','SA','SF%','GF','GA','GF%','xGF','xGA','xGF%','SCF','SCA','SCF%',
                    'SCSF','SCSA','SCSF%','SCGF','SCGA','SCGF%','SCSH%','SCSV%','HDCF','HDCA','HDCF%',
                    'HDSF','HDSA','HDSF%','HDGF','HDGA','HDGF%','HDSH%','HDSV%','MDCF','MDCA','MDCF%',
                    'MDSF','MDSA','MDSF%','MDGF','MDGA','MDGF%','MDSH%','MDSV%','LDCF','LDCA','LDCF%',
                    'LDSF','LDSA','LDSF%','LDGF','LDGA','LDGF%','LDSH%','LDSV%','SH%','SV%','PDO','ML',
                    'Units','Winner']
    df.columns = column_names
    df = df.drop('index', axis=1)
    return df

def getTodayGames(df):
    today = df[df['Date'] == 'January 13, 2024']

    return today


def main():
    game_results = getGames()
    temp_games = game_results
    game_results = game_results[game_results['Date'] != 'January 13, 2024']

    team_encoder = LabelEncoder()

    team_encoder.fit(game_results['Visitor'])
    game_results['Visistor_e'] = team_encoder.transform(game_results['Visitor'])
    game_results['Home_e'] = team_encoder.transform(game_results['Home'])
    game_results['Winner_e'] = team_encoder.transform(game_results['Winner'])

    X = game_results.drop(columns=['Date', 'Visitor', 'Home', 'Winner', 'Winner_e', 'ML'])
    y = game_results['Winner_e']


    unlabelled = getTodayGames(temp_games)
    unlabelled['Visistor_e'] = team_encoder.transform(unlabelled['Visitor'])
    unlabelled['Home_e'] = team_encoder.transform(unlabelled['Home'])
    X_unlabelled = unlabelled.drop(columns=['Date', 'Visitor', 'Home', 'Winner', 'ML'])

    #Training random forest model 
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=6) #best 6, 52
    X_train.fillna(X_train.mean(), inplace = True)
    X_test.fillna(X_train.mean(), inplace = True)

    rf_model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=3000, min_samples_leaf=5, random_state=35, bootstrap=False, n_jobs=-1) #best 35
    )
    rf_model.fit(X_train, y_train)

    # mlp_model = make_pipeline(                                                          #mlp model
    #     StandardScaler(),
    #     MLPClassifier(hidden_layer_sizes=(115,80,40), max_iter=300, activation = 'identity',solver='adam',random_state=23)
    # )
    # mlp_model = mlp_model.fit(X_train, y_train)

    #scoring random forest model
    accuracy = rf_model.score(X_train, y_train)
    test_accuracy = rf_model.score(X_test, y_test)
    print(f'Train Accuracy: {accuracy}')
    print(f'Test Accuracy: {test_accuracy}')
    predictions = rf_model.predict(X_unlabelled)
    print(team_encoder.inverse_transform(predictions))
    pd.Series(team_encoder.inverse_transform(predictions)).to_csv("jan13-2024.csv", index=False, header=False)

main()