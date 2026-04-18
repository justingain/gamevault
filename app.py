from flask import Flask, render_template, request, redirect, url_for
from models import db, Game, PlaySession

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

        if not game.title or not game.platform:
            return render_template(
                "edit_game.html",
                game=game,
                error="Title and Platform are required."
            )

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

@app.route("/games/<int:game_id>")
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    sessions = PlaySession.query.filter_by(game_id=game.id).order_by(PlaySession.id.desc()).all()

    total_minutes = sum(session.duration_minutes for session in sessions)

    return render_template(
        "game_detail.html",
        game=game,
        sessions=sessions,
        total_minutes=total_minutes
    )

@app.route("/games/<int:game_id>/sessions/add", methods=["GET", "POST"])
def add_play_session(game_id):
    game = Game.query.get_or_404(game_id)

    if request.method == "POST":
        session_date = request.form.get("session_date", "").strip()
        duration_raw = request.form.get("duration_minutes", "").strip()
        notes = request.form.get("notes", "").strip()

        if not session_date or not duration_raw:
            return render_template(
                "add_play_session.html",
                game=game,
                error="Date and duration are required."
            )
        
        try:
            duration_minutes = int(duration_raw)
            if duration_minutes <= 0:
                raise ValueError
        except ValueError:
            return render_template(
                "add_play_session.html",
                game=game,
                error="Duration must be a positve whole number"
            )
        
        new_session = PlaySession(
            session_date=session_date,
            duration_minutes=duration_minutes,
            notes=notes if notes else None,
            game_id=game.id
        )

        db.session.add(new_session)
        db.session.commit()

        return redirect(url_for("game_detail", game_id=game.id))
    
    return render_template("add_play_session.html", game=game, error=None)

@app.route("/sessions/delete/<int:session_id>", methods=["POST"])
def delete_play_session(session_id):
    session = PlaySession.query.get_or_404(session_id)
    game_id = session.game_id

    db.session.delete(session)
    db.session.commit()

    return redirect(url_for("game_detail", game_id=game_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="::", port=5001, debug=True, use_reloader=False)