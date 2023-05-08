from flask import Flask, render_template, url_for, request, redirect
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats
import requests
import json
import datetime
import pandas as pd

today = datetime.date.today()
year = today.year

app = Flask(__name__)

all_players = players.get_players()
all_teams = teams.get_teams()

def get_players_career(player_name):
    # get player id from balldontlie api
    response = requests.get("https://www.balldontlie.io/api/v1/players?search=" + player_name)
    if response.status_code == 200:
        bdl_id = json.loads(response)["data"][0]["id"]
    else:
        return None

    # get player career stats from balldontlie api
    stats = []
    for season_year in range(1946, year):
        response = requests.get("https://www.balldontlie.io/api/v1/season_averages?player_ids[]=" + bdl_id + "&season=" + str(season_year))
        if response.status_code == 200:
            if json.loads(response)["data"]:
                to_add = json.loads(response)["data"][0]
                to_add["season"] = f"{season_year}-{season_year+1}"
                stats.append(to_add)
    
    return stats


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/player/search", methods=["POST", "GET"])
def player_search():
    player_not_found = False
    if request.method == "POST":
        player_name = request.form["player-name"]

        if player_name == "":
            return redirect("/player/search")

        try:
            player = [p for p in all_players if p['full_name'].lower() == player_name.lower()][0]
            player_id = str(player['id'])
            return redirect("/player/" + player_id)
        except:
            player_not_found = True

    return render_template("player_search.html", player_not_found=player_not_found)            

    
@app.route("/player/<player_id>")
def player(player_id):
    player_name = [p for p in all_players if p['id'] == int(player_id)][0]['full_name']
    # career = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
    # player_info = career.get_data_frames()[0]
    career_stats = get_players_career(player_name)
    if career_stats:
        player_info = pd.DataFrame(career_stats)
        return render_template("player.html", player_name=player_name, player_info=player_info)
    else:
        return render_template("player.html", player_name=player_name, player_info=None)


@app.route("/team/search", methods=["POST", "GET"])
def team_search():
    team_not_found = False
    if request.method == "POST":
        team_name = request.form["team-name"]

        if team_name == "":
            return redirect("/team/search")

        try:
            team = [t for t in all_teams if t['full_name'].lower() == team_name.lower()][0]
            team_id = str(team['id'])
            return redirect("/team/" + team_id)
        except:
            team_not_found = True

    return render_template("team_search.html", team_not_found=team_not_found)            

    
@app.route("/team/<team_id>")
def team(team_id):
    team_info = [t for t in all_teams if t['id'] == int(team_id)][0]
    
    return render_template("team.html", team_info=team_info)
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")