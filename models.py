from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Backlog")
    rating = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Game {self.title}>"
        
class PlaySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)

    def __repr__(self):
        return f"<PlaySession {self.session_date} - {self.duration_minutes} min>"