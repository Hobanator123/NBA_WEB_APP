from flask import Flask, render_template, request, redirect
from nba_api.stats.static import players, teams
import json
from nba_requests import get_team_roster, get_player_averages, get_player_season


app = Flask(__name__)

all_players = players.get_players()
player_names = [player["full_name"] for player in all_players]
all_teams = teams.get_teams()
team_names = [team["full_name"] for team in all_teams]


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

    return render_template("player_search.html", players=player_names, player_not_found=player_not_found)

    
@app.route("/player/<player_id>")
def player(player_id):
    player_name = [p for p in all_players if p['id'] == int(player_id)][0]['full_name']
    try:
        player_career_averages = get_player_averages(player_name, player_id).sort_values(by=["GROUP_VALUE"], ascending=False)
    except json.decoder.JSONDecodeError:
        return render_template("player_search.html", players=player_names, player_not_found=True)
    
    return render_template("player.html", player_id=player_id, player_name=player_name, player_info=player_career_averages)


@app.route("/player/<player_id>/<season_id>")
def player_season(player_id, season_id):
    player_name = [p for p in all_players if p['id'] == int(player_id)][0]['full_name']
    player_games = get_player_season(player_name, player_id, season_id)
    player_season_overall = player_games[["PTS", "REB", "AST", "STL", "BLK", "TOV", "MIN"]].mean().round(2)
    return render_template("player_season.html", player_name=player_name, player_games=player_games, player_avg=player_season_overall, season=season_id)


@app.route("/team/list", methods=["POST", "GET"])
def team_list():
    return render_template("team_list.html", all_teams=all_teams)


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


@app.route("/team/<team_id>")
def team(team_id):
    team_info = [t for t in all_teams if t['id'] == int(team_id)][0]

    team_roster_df = get_team_roster(team_id)

    return render_template("team.html", team_info=team_info, team_ros=team_roster_df)

    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")