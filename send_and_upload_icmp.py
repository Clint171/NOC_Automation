from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import csv
import platform
import time
from datetime import datetime

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
    """Check routers, update CSV file with status, last updated timestamp, and down devices."""
    routers = []
    down_devices = []
    total_devices = 0

    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames

        # Add missing columns
        if "Status" not in fieldnames:
            fieldnames.append("Status")
        if "Last Updated" not in fieldnames:
            fieldnames.append("Last Updated")

        for row in reader:
            if row["IP"] == '':
                break
            ip = row["IP"]
            print(f"Pinging {ip} ({row['Name']})...")
            status = "1" if ping_router(ip) else "0"
            row["Status"] = status
            row["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if status == "0":
                down_devices.append(row)

            routers.append(row)
            total_devices += 1

    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routers)

        # Append devices down summary at the end of the file
        if down_devices:
            file.write("\nDevices Down Summary\n")
            writer = csv.DictWriter(file, fieldnames=["Name", "IP" , "Status" , "Last Updated"])
            writer.writeheader()
            writer.writerows(down_devices)
        
        file.write("\nTotal devices,"+str(total_devices)+"\n")
        file.write("Devices up,"+ str(total_devices-len(down_devices))+","+str(round((total_devices-len(down_devices))*(100/total_devices), 2))+"\n")
        file.write("Devices down,"+ str(len(down_devices))+","+str(round((len(down_devices))*(100/total_devices), 2))+"\n")

    print("CSV file updated successfully.")
    print("Summary")
    print("-------")
    print("\nTotal devices,"+str(total_devices)+",Percentage\n")
    print("Devices up,"+ str(total_devices-len(down_devices))+","+str(round((total_devices-len(down_devices))*(100/total_devices), 2))+"\n")
    print("Devices down,"+ str(len(down_devices))+","+str(round((len(down_devices))*(100/total_devices), 2))+"\n")
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
