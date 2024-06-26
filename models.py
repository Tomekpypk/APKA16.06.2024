from datetime import datetime
from blog import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'


class CaloricDemand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protein = db.Column(db.Float)
    fat = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)

class TrainingProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    old_PR_bench_press = db.Column(db.Float)
    new_PR_bench_press = db.Column(db.Float)
    old_PR_deadlift = db.Column(db.Float)
    new_PR_deadlift = db.Column(db.Float)
    old_PR_row = db.Column(db.Float)
    new_PR_row = db.Column(db.Float)
    old_PR_squat = db.Column(db.Float)
    new_PR_squat = db.Column(db.Float)

class ExerciseRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(128), nullable=False)
    best_record = db.Column(db.Float, nullable=False)



class BodyMeasurements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Dodajemy user_id jako klucz obcy
    measurement_date = db.Column(db.DateTime, default=datetime.utcnow)
    shoulders = db.Column(db.Float)
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    biceps = db.Column(db.Float)
    hips = db.Column(db.Float)
    thighs = db.Column(db.Float)
    calves = db.Column(db.Float)

    user = db.relationship('User', backref=db.backref('body_measurements', lazy=True))  # Relacja z modelem User

    def __repr__(self):
        return '<BodyMeasurements {}>'.format(self.id)


"""from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    # Dodaj inne pola wg potrzeb
"""
