from flask import Flask, render_template, url_for, request, redirect
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats

app = Flask(__name__)

all_players = players.get_players()
all_teams = teams.get_teams()

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
    career = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=100)
    player_info = career.get_data_frames()[0]
    return render_template("player.html", player_name=player_name, player_info=player_info)


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
    app.run(debug=False, host="0.0.0.0")