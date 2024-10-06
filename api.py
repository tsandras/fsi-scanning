from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
import csv

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
    name = db.Column(db.String(250), nullable=False)

class CompoProduct(db.Model):
    __tablename__ = 'compoproduct'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer)

class RepItem(db.Model):
    __tablename__ = 'repitem'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.Integer, nullable=True)
    scanned = db.Column(db.Integer, nullable=True)


def read_report_preview_lock(identifier):
    try:
        with open(os.getenv('PATH_TO_LOCK_FILE'), 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == identifier:
                    return row[1]  # Retourner le store_id
        return None
    except FileNotFoundError:
        print(f"Le fichier n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier : {e}")
        return None

@app.route('/api/report_preview', methods=['POST'])
def report_preview():
    if request.is_json:
        data = request.get_json()
        barcode = data.get('barcode')
        identifier = data.get('identifier')
        print(identifier)
        # updating the report preview
        if read_report_preview_lock(identifier):
            store_id = read_report_preview_lock(identifier)
            if store_id is None:
                return {'error': 'Store ID is not set in lock file'}, 400
            store_id = int(store_id)
            product = Product.query.filter_by(barcode=barcode).first()
            compo_product = CompoProduct.query.filter_by(barcode=barcode).first()
            if product is None and compo_product is None:
                return {'error': 'Product with this barcode not found'}, 404
            if product:
                repitem_entry = RepItem.query.filter_by(store_id=store_id, product_id=product.id).first()
            else:
                repitem_entry = RepItem.query.filter_by(store_id=store_id, product_id=compo_product.product_id).first()
            if repitem_entry is not None:
                if repitem_entry.scanned is None:
                    repitem_entry.scanned = 0
                if product:
                    repitem_entry.scanned += 1
                else:
                    repitem_entry.scanned += compo_product.quantity
                db.session.commit()

        return {'message': 'Success'}, 200
    else:
        return {'error': 'The request payload is not in JSON format'}

@app.route('/api/stock', methods=['POST'])
def stock():
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