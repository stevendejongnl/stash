import os
import json
from uuid import uuid4
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

# Optional: load .env in development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'products.json')

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)

# Database configuration (optional)
from flask_migrate import Migrate
from stash_app.models import db, Product

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate = Migrate(app, db)
else:
    # keep db-related names available but not initialized
    db = None


def read_products():
    # If DB is configured, read from DB
    if DATABASE_URL and db is not None:
        try:
            with app.app_context():
                products = [p.to_dict() for p in Product.query.order_by(Product.created_at.desc()).all()]
                return products
        except Exception:
            # fallback to file
            pass

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def write_products(products):
    # Only used when file-based storage is active
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(read_products())

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    url = (data.get('url') or '').strip()
    if not title or not url:
        return jsonify({'error': 'title and url are required'}), 400

    product = {
        'id': str(uuid4()),
        'title': title,
        'url': url,
        'price': (data.get('price') or '').strip(),
        'image': (data.get('image') or '').strip(),
        'notes': (data.get('notes') or '').strip(),
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }

    # If DB is configured, insert into DB
    if DATABASE_URL and db is not None:
        try:
            with app.app_context():
                p = Product(
                    id=product['id'],
                    title=product['title'],
                    url=product['url'],
                    price=product['price'],
                    image=product['image'],
                    notes=product['notes'],
                    created_at=datetime.utcnow()
                )
                db.session.add(p)
                db.session.commit()
                return jsonify(p.to_dict()), 201
        except Exception:
            # fallback to file-based on error
            pass

    products = read_products()
    products.insert(0, product)
    write_products(products)
    return jsonify(product), 201

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    # If DB configured, try to delete from DB
    if DATABASE_URL and db is not None:
        try:
            with app.app_context():
                p = Product.query.get(product_id)
                if not p:
                    return jsonify({'error': 'not found'}), 404
                db.session.delete(p)
                db.session.commit()
                return jsonify({'success': True})
        except Exception:
            pass

    products = read_products()
    new_products = [p for p in products if p.get('id') != product_id]
    if len(new_products) == len(products):
        return jsonify({'error': 'not found'}), 404
    write_products(new_products)
    return jsonify({'success': True})

if __name__ == '__main__':
    # development server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)