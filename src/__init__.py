from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED
)
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api_key = os.environ.get('API_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

@app.route('/api/v1/players/', methods=['GET', 'POST'])
def get_all_players():
    if request.method == 'GET':
        all_players = Player.query.order_by(Player.score.desc()).all()
        data = []

        for player in all_players:
            data.append({
                'score': player.score,
                'id': player.id,
                'created_at': player.created_at,
                'updated_at': player.updated_at,
                'username': player.username,
            })

        return jsonify({'data': data}), HTTP_200_OK
    else:
        username = request.json.get('username')
        score = request.json.get('score')
        player = Player(username=username, score=score)
        db.session.add(player)
        db.session.commit()

        return jsonify({
            'score': player.score,
            'id': player.id,
            'created_at': player.created_at,
            'updated_at': player.updated_at,
            'username': player.username,
        }), HTTP_201_CREATED

@app.route('/api/v1/player/<int:id>/', methods=['DELETE'])
def delete_player(id):
    provided_api_key = request.headers.get('API_KEY')

    if provided_api_key != api_key:
        return jsonify({'message': 'Invalid API key'}), HTTP_401_UNAUTHORIZED
    player = Player.query.get(id)
    
    if not player:
        return jsonify({'message': 'Player not found'}), HTTP_404_NOT_FOUND

    db.session.delete(player)
    db.session.commit()

    return jsonify({'message': f"Player with the ID of {id} has been deleted successfully"}), HTTP_200_OK, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run()
