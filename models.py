from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # head, admin, user
    name = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    branch_code = db.Column(db.String(20))
    department = db.Column(db.String(50))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(200))
    status = db.Column(db.String(50), default='Pending') # Pending, In Progress, Resolved, Rejected
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    head_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_role = db.Column(db.String(10))  # head/admin/user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
