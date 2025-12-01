from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# db instance will be created in app.py and imported here
db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=True)
    image = db.Column(db.String, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        # match the JSON shape used elsewhere
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'price': self.price or '',
            'image': self.image or '',
            'notes': self.notes or '',
            'created_at': (self.created_at.isoformat() + 'Z') if self.created_at else None
        }

