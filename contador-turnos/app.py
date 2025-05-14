from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turns.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#
class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desk = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def display():
    return render_template('display.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/get_status')
def get_status():
    # Obtener el último turno general
    last_turn = Turn.query.order_by(Turn.id.desc()).first()
    
    # Obtener último turno de cada mesa
    desks = {}
    for desk_num in range(1, 5):
        desk_last = Turn.query.filter_by(desk=desk_num).order_by(Turn.id.desc()).first()
        desks[desk_num] = desk_last.id if desk_last else 0
    
    return jsonify({
        'current_turn': last_turn.id if last_turn else 0,
        'current_desk': last_turn.desk if last_turn else None,
        'desks': desks
    })

@app.route('/next_turn', methods=['POST'])
def next_turn():
    desk = request.json['desk']
    
    # Crear nuevo turno
    new_turn = Turn(desk=desk)
    db.session.add(new_turn)
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)