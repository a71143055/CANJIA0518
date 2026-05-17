from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from config import Config

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    microsoft_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    documents = db.relationship('Document', backref='author', lazy=True, cascade='all, delete-orphan')
    field_memberships = db.relationship('FieldMembership', backref='user', lazy=True, cascade='all, delete-orphan')

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='field', lazy=True, cascade='all, delete-orphan')
    memberships = db.relationship('FieldMembership', backref='field', lazy=True, cascade='all, delete-orphan')

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)

class FieldMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'field_id', name='unique_user_field'),)
