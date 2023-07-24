import requests
from datetime import datetime
import pandas as pd
import json

# Headers needed for the NBA stats website
headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}

# Base URL for NBA stats API
base_url = "https://stats.nba.com/stats"

# Current season for NBA
CURR_SEASON = str(datetime.now().year) + "-" + str(datetime.now().year + 1)[2:]

# Send request to given URL with retries in case of timeout
def send_request(url):
    response = False
    for _ in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response:
                return response
        except requests.exceptions.ReadTimeout:
            print("Exception caught, trying again...")

    return response

# Get team roster for given team ID
def get_team_roster(team_id):
    print(f"Parsing roster for team_id: {team_id}")
    url = f"{base_url}/commonteamroster?LeagueID=00&Season=2022-23&TeamID={team_id}"
    response = send_request(url)
    if response:
        results = json.loads(response.content)['resultSets']
        roster = [result for result in results if result["name"] == "CommonTeamRoster"][0]
        columns = roster["headers"]
        data = roster["rowSet"]
        return pd.DataFrame(data, columns=columns)
    
    return False

# Get player averages for given player name and player ID
def get_player_averages(player_name, player_id):
    print(f"Processing player: {player_name}")
    url = f"{base_url}/playerdashboardbyyearoveryearcombined?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerID={player_id}&PlusMinus=N&Rank=N&Season={CURR_SEASON}&SeasonSegment=&SeasonType=Regular%20Season&ShotClockRange=&VsConference=&VsDivision="
    response = send_request(url)
    if response:
        results = json.loads(response.content)['resultSets']
        yearly_averages = [result for result in results if result["name"] == "ByYearBasePlayerDashboard"][0]
        columns = yearly_averages["headers"]
        data = yearly_averages["rowSet"]

        yearly_averages_df = pd.DataFrame(data, columns=columns)
        yearly_averages_df["PLAYER_NAME"] = player_name
        yearly_averages_df["PLAYER_ID"] = str(player_id)
        # If a player plays for multiple teams in a a season, an extra TOTAL row is added
        yearly_averages_df = yearly_averages_df.loc[yearly_averages_df["TEAM_ID"] != -1]

        return yearly_averages_df.fillna(0.00).round(2).sort_values(by=["GROUP_VALUE"], ascending=False)
    
    return False

# Get season stats for given player name, player ID and season ID
def get_player_season(player_name, player_id, season_id):
    print(f"Parsing player: {player_name} for season: {season_id}")
    url = f"{base_url}/playergamelog?DateFrom=&DateTo=&LeagueID=00&PlayerID={player_id}&Season={season_id}&SeasonType=Regular%20Season"
    response = send_request(url)
    if response:
        games = json.loads(response.content)['resultSets'][0]
        columns = games["headers"]
        data = games["rowSet"]
        return pd.DataFrame(data, columns=columns).fillna(0.00).round(2)
    
    return False

