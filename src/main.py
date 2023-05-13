from flask import Flask, render_template, request, redirect
from nba_api.stats.static import players, teams
from nba_requests import get_team_roster, get_player_averages, get_player_season
import json
import pandas as pd


app = Flask(__name__)

# Retrieve all NBA players and teams using the `nba_api` module
all_players = players.get_players()
player_names = [player["full_name"] for player in all_players]
all_teams = teams.get_teams()
team_names = [team["full_name"] for team in all_teams]


@app.route("/")
def home():
    return render_template("home.html")


# Define the route for searching players. If a POST request is made to this route, it attempts to find the player 
# If the player is found, it redirects to the player's page; if not, it renders the player_search.html template with an error message
@app.route("/player/search", methods=["POST", "GET"])
def player_search():
    if request.method == "POST":
        player_name = request.form["player-name"]

        if player_name == "":
            return redirect("/player/search")

        try:
            player = [p for p in all_players if p['full_name'].lower() == player_name.lower()][0]
            player_id = str(player['id'])
            return redirect("/player/" + player_id)
        except:
            return render_template("player_search.html", players=player_names, player_not_found=True)
    else:
        return render_template("player_search.html", players=player_names, player_not_found=False)

    
# Define a route for individual players based on their ID. This route fetches the player's career averages 
# and renders them on the player.html template
@app.route("/player/<player_id>")
def player(player_id):
    player_name = [p for p in all_players if p['id'] == int(player_id)][0]['full_name']
    try:
        player_career_averages = get_player_averages(player_name, player_id)
    except json.decoder.JSONDecodeError:
        return render_template("player_search.html", players=player_names, player_not_found=True)
    
    if not isinstance(player_career_averages, pd.DataFrame):
        return render_template("timeout.html")

    return render_template("player.html", player_id=player_id, player_name=player_name, player_info=player_career_averages)


# Define a route for displaying the stats of a player for a specific season.
# This route fetches the player's stats for the given season and renders them on the player_season.html template
@app.route("/player/<player_id>/<season_id>")
def player_season(player_id, season_id):
    player_name = [p for p in all_players if p['id'] == int(player_id)][0]['full_name']
    player_games = get_player_season(player_name, player_id, season_id)

    if not isinstance(player_games, pd.DataFrame):
        return render_template("timeout.html")
    
    player_season_overall = player_games[["PTS", "REB", "AST", "STL", "BLK", "TOV", "MIN"]].mean().round(2)
    return render_template("player_season.html", player_name=player_name, player_games=player_games, player_avg=player_season_overall, season=season_id)


# Define a route for displaying a list of all NBA teams. This route renders the team_list.html template 
# with a list of all teams
@app.route("/team/list", methods=["POST", "GET"])
def team_list():
    return render_template("team_list.html", all_teams=all_teams)


# Define a route for searching teams. If a POST request is made to this route, it attempts to find the team 
# If the team is found, it redirects to the team's page; if not, it renders the team_search.html template with an error message
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

    return render_template("team_search.html", teams=team_names, team_not_found=team_not_found)            


# Define a route for individual teams based on their ID. This route fetches the team's roster 
# and renders it on the team.html template
@app.route("/team/<team_id>")
def team(team_id):
    team_info = [t for t in all_teams if t['id'] == int(team_id)][0]

    team_roster_df = get_team_roster(team_id)

    if not isinstance(team_roster_df, pd.DataFrame):
        return render_template("timeout.html")
    
    return render_template("team.html", team_info=team_info, team_ros=team_roster_df)

    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")