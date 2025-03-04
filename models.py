from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Region(db.Model):
    __tablename__ = "regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    counties = db.relationship("County", backref="region", cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<Region {self.name}>"


class County(db.Model):
    __tablename__ = "counties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=False)
    devices = db.relationship("Device", backref="county", cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<County {self.name}>"


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), unique=True, nullable=False)
    county_id = db.Column(db.Integer, db.ForeignKey("counties.id"), nullable=True)
    statuses = db.relationship("DeviceStatus", backref="device", cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<Device {self.name} - {self.ip}>"


class DeviceStatus(db.Model):
    __tablename__ = "device_statuses"
    id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(50), db.ForeignKey("devices.ip"), nullable=False)
    status = db.Column(db.Boolean, nullable=False)  # 1 (Up), 0 (Down)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    comments = db.relationship("Comment", backref="device_status", cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<Status {self.device_ip} - {'Up' if self.status else 'Down'}>"


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey("device_statuses.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Comment {self.text[:30]}...>"
