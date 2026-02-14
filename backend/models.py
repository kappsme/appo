"""
Database models for the appointment booking system
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Service(db.Model):
    """Service model for different types of appointments"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, default=60)  # in minutes
    price = db.Column(db.Float, default=0.0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'price': self.price,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Appointment(db.Model):
    """Appointment model with recurrence support"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    client = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    recurrence = db.Column(db.String(20), default='none')  # none, weekly, monthly
    recurrence_end = db.Column(db.Date)
    parent_appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    status = db.Column(db.String(20), default='active')  # active, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for recurring appointments
    children = db.relationship('Appointment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.strftime('%H:%M') if self.time else None,
            'client': self.client,
            'phone': self.phone,
            'service_id': self.service_id,
            'service_name': self.service.name if self.service else None,
            'recurrence': self.recurrence,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None,
            'parent_appointment_id': self.parent_appointment_id,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Availability(db.Model):
    """Availability configuration for each day of the week"""
    __tablename__ = 'availability'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RecurrenceRule(db.Model):
    """Rules for recurring appointments"""
    __tablename__ = 'recurrence_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    interval = db.Column(db.Integer, default=1)  # every X days/weeks/months
    count = db.Column(db.Integer)  # number of occurrences
    until = db.Column(db.Date)  # end date
    by_day = db.Column(db.String(50))  # e.g., "MO,WE,FR" for weekly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'frequency': self.frequency,
            'interval': self.interval,
            'count': self.count,
            'until': self.until.isoformat() if self.until else None,
            'by_day': self.by_day,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
