from flask import Flask, request, jsonify
from models import db, Region, County, Device, DeviceStatus, Comment
from config import Config
from datetime import datetime
import csv
from io import StringIO
from sqlalchemy import desc

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    return "Network Monitoring API"

# Regions
@app.route('/regions', methods=['GET'])
def get_regions():
    regions = Region.query.all()
    return jsonify([{"id": r.id, "name": r.name} for r in regions])

@app.route('/regions/<int:region_id>', methods=['GET'])
def get_region(region_id):
    region = Region.query.get_or_404(region_id)
    return jsonify({"id": region.id, "name": region.name})

# Counties
@app.route('/counties', methods=['GET'])
def get_counties():
    counties = County.query.all()
    return jsonify([{"id": c.id, "name": c.name, "region_id": c.region_id} for c in counties])

@app.route('/counties/<int:county_id>', methods=['GET'])
def get_county(county_id):
    county = County.query.get_or_404(county_id)
    return jsonify({"id": county.id, "name": county.name, "region_id": county.region_id})

# Devices
@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{"id": d.id, "name": d.name, "ip": d.ip, "county_id": d.county_id} for d in devices])

@app.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify({"id": device.id, "name": device.name, "ip": device.ip, "county_id": device.county_id})

# Device Statuses (Latest Status Only)
@app.route('/device_statuses', methods=['GET'])
def get_device_statuses():
    # Get the latest status for each device
    latest_statuses = db.session.query(DeviceStatus).distinct(DeviceStatus.device_ip).order_by(
        DeviceStatus.device_ip, desc(DeviceStatus.time))
    return jsonify([{
        "id": s.id,
        "device_ip": s.device_ip,
        "status": s.status,
        "time": s.time.isoformat(),
        "comments": [{"id": c.id, "text": c.text} for c in s.comments]
    } for s in latest_statuses])

@app.route('/device_statuses/<int:status_id>', methods=['GET'])
def get_device_status(status_id):
    status = DeviceStatus.query.get_or_404(status_id)
    return jsonify({
        "id": status.id,
        "device_ip": status.device_ip,
        "status": status.status,
        "time": status.time.isoformat(),
        "comments": [{"id": c.id, "text": c.text} for c in status.comments]
    })

# Comments
@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify([{"id": c.id, "status_id": c.status_id, "text": c.text} for c in comments])

@app.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify({"id": comment.id, "status_id": comment.status_id, "text": comment.text})

# Device Management Endpoints
@app.route('/devices', methods=['POST'])
def add_device():
    data = request.json
    new_device = Device(name=data['name'], ip=data['ip'], county_id=data.get('county_id'))
    db.session.add(new_device)
    db.session.commit()
    return jsonify({"message": "Device added successfully"}), 201

@app.route('/devices/<int:device_id>', methods=['PUT'])
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.json
    device.name = data.get('name', device.name)
    device.ip = data.get('ip', device.ip)
    device.county_id = data.get('county_id', device.county_id)
    db.session.commit()
    return jsonify({"message": "Device updated successfully"})

@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"message": "Device deleted successfully"})

@app.route('/devices/upload', methods=['POST'])
def upload_devices():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        for row in csv_reader:
            new_device = Device(name=row['name'], ip=row['ip'])
            db.session.add(new_device)
        db.session.commit()
        return jsonify({"message": "Devices uploaded successfully"}), 201
    return jsonify({"error": "File must be a CSV"}), 400

# County and Region Management Endpoints
@app.route('/counties', methods=['POST'])
def add_county():
    data = request.json
    new_county = County(name=data['name'], region_id=data['region_id'])
    db.session.add(new_county)
    db.session.commit()
    return jsonify({"message": "County added successfully"}), 201

@app.route('/counties/<int:county_id>', methods=['DELETE'])
def delete_county(county_id):
    county = County.query.get_or_404(county_id)
    db.session.delete(county)
    db.session.commit()
    return jsonify({"message": "County deleted successfully"})

@app.route('/regions', methods=['POST'])
def add_region():
    data = request.json
    new_region = Region(name=data['name'])
    db.session.add(new_region)
    db.session.commit()
    return jsonify({"message": "Region added successfully"}), 201

@app.route('/regions/<int:region_id>', methods=['DELETE'])
def delete_region(region_id):
    region = Region.query.get_or_404(region_id)
    db.session.delete(region)
    db.session.commit()
    return jsonify({"message": "Region deleted successfully"})

# Reporting Endpoints
@app.route('/reports/daily')
def daily_report():
    # Implement logic to generate daily report
    return jsonify({"message": "Daily report generated"})

@app.route('/reports/monthly')
def monthly_report():
    # Implement logic to generate monthly report
    return jsonify({"message": "Monthly report generated"})

@app.route('/reports/yearly')
def yearly_report():
    # Implement logic to generate yearly report
    return jsonify({"message": "Yearly report generated"})

if __name__ == '__main__':
    app.run(debug=True)