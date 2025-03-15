import asyncio
import subprocess
import psycopg2
from psycopg2 import pool
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "dbname": "network_monitoring",
    "user": "flask_user",
    "password": "securepassword",
    "host": "localhost",
    "port": "5432",
}

# Connection pool for PostgreSQL
db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

# Function to ping a single device asynchronously
async def ping_device(ip):
    try:
        # Use `ping` command with a timeout of 1 second
        process = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-W", "2", ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return ip, process.returncode == 0  # True if ping succeeds
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return ip, False

# Function to fetch all devices from the database
def fetch_devices():
    conn = db_pool.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, ip FROM devices")
    devices = cur.fetchall()
    db_pool.putconn(conn)
    return devices

# Function to update device status and log ping history
def update_device_status(device_id, status):
    conn = db_pool.getconn()
    cur = conn.cursor()
    try:
        # Update device status
        cur.execute("""
            UPDATE devices
            SET status = %s
            WHERE id = %s
        """, ("up" if status else "down", device_id))

        # Insert into ping_histories
        cur.execute("""
            INSERT INTO ping_histories (device, status, date)
            VALUES (%s, %s, %s)
        """, (device_id, "up" if status else "down", datetime.now()))

        conn.commit()
    except Exception as e:
        print(f"Error updating database for device {device_id}: {e}")
        conn.rollback()
    finally:
        db_pool.putconn(conn)

# Main function to ping all devices
async def ping_all_devices():
    devices = fetch_devices()
    tasks = [ping_device(ip) for _, ip in devices]
    results = await asyncio.gather(*tasks)

    # Map IPs back to device IDs
    ip_to_device_id = {ip: device_id for device_id, ip in devices}

    # Update database with results
    for ip, status in results:
        device_id = ip_to_device_id.get(ip)
        if device_id:
            update_device_status(device_id, status)

# Run the script
if __name__ == "__main__":
    asyncio.run(ping_all_devices())