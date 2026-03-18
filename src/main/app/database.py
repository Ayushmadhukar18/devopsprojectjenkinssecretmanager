from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Secret(db.Model):
    __tablename__ = "secrets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    encrypted_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    @property
    def days_until_expiry(self):
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    @property
    def status(self):
        if self.expires_at is None:
            return "active"
        days = self.days_until_expiry
        if days == 0:
            return "expired"
        if days <= 7:
            return "expiring"
        return "active"

    def __repr__(self):
        return f"<Secret {self.name}>"


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)   # CREATE, ROTATE, DELETE, VIEW
    secret_name = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), default="admin")
    details = db.Column(db.String(255), default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.secret_name}>"
