from flask import Flask, request, jsonify
from models import db, Region, County, Device, DeviceStatus, Comment
from config import Config
from datetime import datetime, timedelta
import csv
from io import StringIO
from sqlalchemy import desc , case , func

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
# Helper function to calculate uptime percentage
def calculate_uptime_percentage(statuses):
    total_pings = len(statuses)
    if total_pings == 0:
        return 0.0
    uptime_count = sum(status for status in statuses)
    return (uptime_count / total_pings) * 100

# Daily Report with Grouping
@app.route('/reports/daily', methods=['GET'])
def daily_report():
    now = datetime.utcnow()
    start_time = now - timedelta(hours=24)

    # Query to get hourly uptime for devices, counties, regions, and overall
    hourly_data = db.session.query(
        DeviceStatus.device_ip,
        County.name.label('county_name'),
        Region.name.label('region_name'),
        func.date_trunc('hour', DeviceStatus.time).label('hour'),
        DeviceStatus.status
    ).join(Device, DeviceStatus.device_ip == Device.ip
    ).join(County, Device.county_id == County.id, isouter=True
    ).join(Region, County.region_id == Region.id, isouter=True
    ).filter(DeviceStatus.time >= start_time
    ).all()

    # Organize data for devices, counties, regions, and overall
    device_results = {}
    county_results = {}
    region_results = {}
    overall_results = {}

    for device_ip, county_name, region_name, hour, status in hourly_data:
        # Device-level grouping
        if device_ip not in device_results:
            device_results[device_ip] = {}
        if hour not in device_results[device_ip]:
            device_results[device_ip][hour] = []
        device_results[device_ip][hour].append(status)

        # County-level grouping
        if county_name:
            if county_name not in county_results:
                county_results[county_name] = {}
            if hour not in county_results[county_name]:
                county_results[county_name][hour] = []
            county_results[county_name][hour].append(status)

        # Region-level grouping
        if region_name:
            if region_name not in region_results:
                region_results[region_name] = {}
            if hour not in region_results[region_name]:
                region_results[region_name][hour] = []
            region_results[region_name][hour].append(status)

        # Overall grouping
        if hour not in overall_results:
            overall_results[hour] = []
        overall_results[hour].append(status)

    # Calculate uptime percentages
    def format_results(data):
        formatted = {}
        for key, hourly_statuses in data.items():
            formatted[key] = {}
            for hour, statuses in hourly_statuses.items():
                formatted[key][hour.isoformat()] = calculate_uptime_percentage(statuses)
        return formatted

    return jsonify({
        "devices": format_results(device_results),
        "counties": format_results(county_results),
        "regions": format_results(region_results),
        "overall": {hour.isoformat(): calculate_uptime_percentage(statuses) for hour, statuses in overall_results.items()}
    })

# Monthly Report with Grouping
@app.route('/reports/monthly', methods=['GET'])
def monthly_report():
    now = datetime.utcnow()
    start_time = datetime(now.year, now.month, 1)

    # Query to get daily uptime for devices, counties, regions, and overall
    daily_data = db.session.query(
        DeviceStatus.device_ip,
        County.name.label('county_name'),
        Region.name.label('region_name'),
        func.date_trunc('day', DeviceStatus.time).label('day'),
        DeviceStatus.status
    ).join(Device, DeviceStatus.device_ip == Device.ip
    ).join(County, Device.county_id == County.id, isouter=True
    ).join(Region, County.region_id == Region.id, isouter=True
    ).filter(DeviceStatus.time >= start_time
    ).all()

    # Organize data for devices, counties, regions, and overall
    device_results = {}
    county_results = {}
    region_results = {}
    overall_results = {}

    for device_ip, county_name, region_name, day, status in daily_data:
        # Device-level grouping
        if device_ip not in device_results:
            device_results[device_ip] = {}
        if day not in device_results[device_ip]:
            device_results[device_ip][day] = []
        device_results[device_ip][day].append(status)

        # County-level grouping
        if county_name:
            if county_name not in county_results:
                county_results[county_name] = {}
            if day not in county_results[county_name]:
                county_results[county_name][day] = []
            county_results[county_name][day].append(status)

        # Region-level grouping
        if region_name:
            if region_name not in region_results:
                region_results[region_name] = {}
            if day not in region_results[region_name]:
                region_results[region_name][day] = []
            region_results[region_name][day].append(status)

        # Overall grouping
        if day not in overall_results:
            overall_results[day] = []
        overall_results[day].append(status)

    # Calculate uptime percentages
    def format_results(data):
        formatted = {}
        for key, daily_statuses in data.items():
            formatted[key] = {}
            for day, statuses in daily_statuses.items():
                formatted[key][day.isoformat()] = calculate_uptime_percentage(statuses)
        return formatted

    return jsonify({
        "devices": format_results(device_results),
        "counties": format_results(county_results),
        "regions": format_results(region_results),
        "overall": {day.isoformat(): calculate_uptime_percentage(statuses) for day, statuses in overall_results.items()}
    })

# Yearly Report with Grouping
@app.route('/reports/yearly', methods=['GET'])
def yearly_report():
    now = datetime.utcnow()
    start_time = datetime(now.year, 1, 1)

    # Query to get monthly uptime for devices, counties, regions, and overall
    monthly_data = db.session.query(
        DeviceStatus.device_ip,
        County.name.label('county_name'),
        Region.name.label('region_name'),
        func.date_trunc('month', DeviceStatus.time).label('month'),
        DeviceStatus.status
    ).join(Device, DeviceStatus.device_ip == Device.ip
    ).join(County, Device.county_id == County.id, isouter=True
    ).join(Region, County.region_id == Region.id, isouter=True
    ).filter(DeviceStatus.time >= start_time
    ).all()

    # Organize data for devices, counties, regions, and overall
    device_results = {}
    county_results = {}
    region_results = {}
    overall_results = {}

    for device_ip, county_name, region_name, month, status in monthly_data:
        # Device-level grouping
        if device_ip not in device_results:
            device_results[device_ip] = {}
        if month not in device_results[device_ip]:
            device_results[device_ip][month] = []
        device_results[device_ip][month].append(status)

        # County-level grouping
        if county_name:
            if county_name not in county_results:
                county_results[county_name] = {}
            if month not in county_results[county_name]:
                county_results[county_name][month] = []
            county_results[county_name][month].append(status)

        # Region-level grouping
        if region_name:
            if region_name not in region_results:
                region_results[region_name] = {}
            if month not in region_results[region_name]:
                region_results[region_name][month] = []
            region_results[region_name][month].append(status)

        # Overall grouping
        if month not in overall_results:
            overall_results[month] = []
        overall_results[month].append(status)

    # Calculate uptime percentages
    def format_results(data):
        formatted = {}
        for key, monthly_statuses in data.items():
            formatted[key] = {}
            for month, statuses in monthly_statuses.items():
                formatted[key][month.isoformat()] = calculate_uptime_percentage(statuses)
        return formatted

    return jsonify({
        "devices": format_results(device_results),
        "counties": format_results(county_results),
        "regions": format_results(region_results),
        "overall": {month.isoformat(): calculate_uptime_percentage(statuses) for month, statuses in overall_results.items()}
    })

if __name__ == '__main__':
    app.run(debug=True)