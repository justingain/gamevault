from flask import Flask, render_template, request, redirect, url_for
from models import db, Game

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gamevault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# App Routes
@app.route("/")
def home():
    return "<h1>GameVault is running</h1><p>Go to <a href='/games'>/games</a></p>"

@app.route("/games")
def games():
    all_games = Game.query.order_by(Game.title.asc()).all()
    return render_template("games.html", games=all_games)


# Add game logic
@app.route("/games/add", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        platform = request.form.get("platform", "").strip()
        status = request.form.get("status", "Backlog").strip()
        rating_raw = request.form.get("rating", "").strip()

        if not title or not platform:
            error = "Title and Platform are required."
            return render_template("add_game.html", error=error)
        
        rating = None
        if rating_raw:
            try:
                rating = int(rating_raw)
            except ValueError:
                error = "Rating must be a whole number."
                return render_template("add_game.html", error=error)

            if rating < 1 or rating > 10:
                error = "Rating must be between 1 and 10."
                return render_template("add_game.html", error=error)
            
        new_game = Game(
            title=title,
            platform=platform,
            status=status,
            rating=rating
        )

        db.session.add(new_game)
        db.session.commit()

        return redirect(url_for("games"))
    
    return render_template("add_game.html", error=None)

# Delete game logic
@app.route("/games/delete/<int:game_id>", methods=["POST"])
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)

    db.session.delete(game)
    db.session.commit()

    return redirect(url_for("games"))

# Edit game logic
@app.route("/games/edit/<int:game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)

    if request.method == "POST":
        game.title = request.form.get("title", "").strip()
        game.platform = request.form.get("platform", "").strip()
        game.status = request.form.get("status", "Backlog").strip()

        rating_raw = request.form.get("rating", "").strip()

        if rating_raw:
            try:
                rating = int(rating_raw)
                if rating < 1 or rating > 10:
                    raise ValueError
                game.rating = rating
            except ValueError:
                return render_template("edit_game.html", game=game, error="Rating must be 1-10")
        else:
            game.rating = None
        
        db.session.commit()

        return redirect(url_for("games"))
    
    return render_template("edit_game.html", game=game, error=None)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="::", port=5001, debug=True, use_reloader=False)