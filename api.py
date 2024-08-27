from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

class EventScanning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)

@app.route('/api/test', methods=['POST'])
def event_scan():
    if request.is_json:
        data = request.get_json()
        barcode = data.get('barcode')
        action = data.get('action')

        new_entry = EventScanning(barcode=barcode, action=action)
        db.session.add(new_entry)
        db.session.commit()

        return {'message': 'Success'}, 200
    else:
        return {'error': 'The request payload is not in JSON format'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)