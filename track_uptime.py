import os
import psycopg2
import datetime

# Database connection details
DB_CONFIG = {
    "dbname": "network_monitoring",
    "user": "flask_user",
    "password": "securepassword",
    "host": "localhost",
    "port": "5432",
}

# Function to check device status using ping
def ping_device(ip):
    response = os.system(f"ping -c 2 {ip} > /dev/null 2>&1")
    return 1 if response == 0 else 0

# Function to update device status and store comments
def update_device_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get all devices
        cursor.execute("SELECT id, ip FROM devices;")
        devices = cursor.fetchall()

        for device_id, ip in devices:
            status = True if ping_device(ip) else False
            timestamp = datetime.datetime.now()
            comment_text = "Device unreachable" if status == 0 else "Device is online"

            # Insert status into the device_statuses table
            cursor.execute(
                "INSERT INTO device_statuses (device_ip, status, time) VALUES (%s, %s, %s) RETURNING id;",
                (ip, status, timestamp),
            )
            status_id = cursor.fetchone()[0]

            # Insert comment into the comments table
            cursor.execute(
                "INSERT INTO comments (status_id, text) VALUES (%s, %s);",
                (status_id, comment_text),
            )

        conn.commit()
        cursor.close()
        conn.close()

        print("Device status and comments updated successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_device_status()