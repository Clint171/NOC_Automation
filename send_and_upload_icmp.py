from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import csv
import platform
import time

# Google Drive setup
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

CSV_FILE = "devices/routers-prod.csv"

def ping_router(ip):
    """Ping a router to check if it's reachable."""
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    command = f"ping {param} {ip}"
    return os.system(command) == 0

def check_routers():
    """Check routers and update the CSV file."""
    routers = []

    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ["Status"] if "Status" not in reader.fieldnames else reader.fieldnames
        for row in reader:
            ip = row["IP"]
            print(f"Pinging {ip} ({row['Name']})...")
            row["Status"] = "1" if ping_router(ip) else "0"
            routers.append(row)

    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routers)

    print("CSV file updated successfully.")
    upload_to_drive()

def upload_to_drive():
    """Upload the CSV file to Google Drive."""
    # Search for existing file and update it, otherwise create new one
    file_list = drive.ListFile({'q': f"title='{CSV_FILE}'"}).GetList()
    
    if file_list:
        file = file_list[0]  # Update existing file
        file.SetContentFile(CSV_FILE)
        file.Upload()
        print("CSV file updated in Google Drive.")
    else:
        file = drive.CreateFile({'title': CSV_FILE})
        file.SetContentFile(CSV_FILE)
        file.Upload()
        print("CSV file uploaded to Google Drive.")


check_routers()