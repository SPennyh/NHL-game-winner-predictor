import pandas as pd
import numpy as np
import requests 
from bs4 import BeautifulSoup 
import csv

def getGames():
    URL = "https://www.naturalstattrick.com/"
    r = requests.get(URL) 
    soup = BeautifulSoup(r.content, 'html.parser')
    quotes =  pd.DataFrame()
   
    #print(soup)

    table = soup.find('div', attrs = {'style':'margin:5px; padding:5px; min-height:25px;'})

    games = pd.DataFrame()
    for row in table.find_all('div', attrs = {'class':'boxscore'}): 
        teams = row.get_text()
        teams  = teams.split('\n')
        temp_games = pd.DataFrame({'away': [teams[1]], 'home': [teams[2]]})
        games = pd.concat([games, temp_games])
        
    games = games.reset_index().drop('index', axis=1)
    
    return games

def main():
    data = pd.read_csv("games (6).csv")
    stats = data[['Team', 'GP', 'SA']]
    stats.loc[:,'SA/GP'] = stats['SA'] / stats['GP']
    stats = stats.sort_values('SA/GP', ascending=False)

    
    games = getGames()


    print(stats)
    print(games)


main()