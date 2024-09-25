from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

class EventScanning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), nullable=True)

class RepItem(db.Model):
    __tablename__ = 'repitem'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.Integer, nullable=True)
    scanned = db.Column(db.Integer, nullable=True)


def read_report_preview_lock():
    try:
        with open(os.getenv('PATH_TO_LOCK_FILE'), 'r') as file:
            return file.strip()
    except FileNotFoundError:
        return None

@app.route('/api/test', methods=['POST'])
def event_scan():
    if request.is_json:
        data = request.get_json()
        barcode = data.get('barcode')
        action = data.get('action')

        # updating the report preview
        if read_report_preview_lock():
            store_id = int(read_report_preview_lock())
            product = Product.query.filter_by(barcode=barcode).first()
            repitem_entry = RepItem.query.filter_by(store_id=store_id, product_id=product.id).first()
            if repitem_entry is not None:
                repitem_entry.scanned += 1
                db.session.commit()

        else: # updating product stock
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