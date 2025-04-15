import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

class Car(db.Model):
    """Модель для хранения данных об автомобилях"""
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    specifications = db.Column(db.Text, nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    
    def __repr__(self):
        return f'<Car {self.name}>'
    
    def to_dict(self):
        """Преобразовать модель в словарь для удобства использования"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'specifications': self.specifications,
            'image': self.image
        }


class Admin(db.Model):
    """Модель для хранения данных администраторов"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Admin {self.username}>'