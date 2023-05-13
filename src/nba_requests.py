import requests
from datetime import datetime
import pandas as pd
import json

headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}


base_url = "https://stats.nba.com/stats"


CURR_SEASON = str(datetime.now().year) + "-" + str(datetime.now().year + 1)[2:]

def get_team_roster(team_id):
    print(f"Parsing roster for team_id: {team_id}")
    url = f"{base_url}/commonteamroster?LeagueID=00&Season=2022-23&TeamID={team_id}"
    response = requests.get(url, headers=headers)
    results = json.loads(response.content)['resultSets']
    roster = [result for result in results if result["name"] == "CommonTeamRoster"][0]
    columns = roster["headers"]
    data = roster["rowSet"]
    return pd.DataFrame(data, columns=columns)

def get_player_averages(player_name, player_id):
    print(f"Processing player: {player_name}")
    url = f"{base_url}/playerdashboardbyyearoveryearcombined?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerID={player_id}&PlusMinus=N&Rank=N&Season={CURR_SEASON}&SeasonSegment=&SeasonType=Regular%20Season&ShotClockRange=&VsConference=&VsDivision="
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ReadTimeout:
        print("exception caught, trying again...")
        response = requests.get(url, headers=headers, timeout=10)
    results = json.loads(response.content)['resultSets']
    yearly_averages = [result for result in results if result["name"] == "ByYearBasePlayerDashboard"][0]
    columns = yearly_averages["headers"]
    data = yearly_averages["rowSet"]

    yearly_averages_df = pd.DataFrame(data, columns=columns)
    yearly_averages_df["PLAYER_NAME"] = player_name
    yearly_averages_df["PLAYER_ID"] = str(player_id)

    return yearly_averages_df.fillna(0.00).round(2)

def get_player_season(player_name, player_id, season_id):
    print(f"Parsing player: {player_name} for season: {season_id}")
    url = f"{base_url}/playergamelog?DateFrom=&DateTo=&LeagueID=00&PlayerID={player_id}&Season={season_id}&SeasonType=Regular%20Season"
    response = requests.get(url, headers=headers)
    games = json.loads(response.content)['resultSets'][0]
    columns = games["headers"]
    data = games["rowSet"]
    return pd.DataFrame(data, columns=columns).fillna(0.00).round(2)

