import os
import psycopg2
import datetime
import concurrent.futures
from typing import List, Tuple

# Database connection details
DB_CONFIG = {
    "dbname": "network_monitoring",
    "user": "flask_user",
    "password": "securepassword",
    "host": "localhost",
    "port": "5432",
}

# Function to check device status using ping
def ping_device(ip: str) -> bool:
    response = os.system(f"ping -c 2 {ip} > /dev/null 2>&1")
    return response == 0

# Function to update device status and store comments in batches
def update_device_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get all devices
        cursor.execute("SELECT id, ip FROM devices;")
        devices = cursor.fetchall()

        # Use ThreadPoolExecutor for parallel pinging
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            future_to_ip = {executor.submit(ping_device, ip): (device_id, ip) for device_id, ip in devices}
            statuses = []
            for future in concurrent.futures.as_completed(future_to_ip):
                device_id, ip = future_to_ip[future]
                status = future.result()
                timestamp = datetime.datetime.now()
                comment_text = "Device is online" if status else "Device unreachable"
                statuses.append((ip, status, timestamp, comment_text))

        # Batch insert statuses and comments
        if statuses:
            status_ids = []
            status_values = [(ip, status, time) for ip, status, time, _ in statuses]
            cursor.executemany(
                "INSERT INTO device_statuses (device_ip, status, time) VALUES (%s, %s, %s) RETURNING id;",
                status_values,
            )
            status_ids = [row[0] for row in cursor.fetchall()]

            comment_values = [(status_id, comment_text) for status_id, (_, _, _, comment_text) in zip(status_ids, statuses)]
            cursor.executemany(
                "INSERT INTO comments (status_id, text) VALUES (%s, %s);",
                comment_values,
            )

        conn.commit()
        cursor.close()
        conn.close()

        print("Device status and comments updated successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_device_status()