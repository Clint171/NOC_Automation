import csv
import os
import platform
import time

def ping_router(ip):
    """Ping a router to check if it's reachable."""
    # Define the ping command based on the OS
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    command = f"ping {param} {ip}"
    
    # Execute the ping command and check the response
    return os.system(command) == 0

def check_routers(csv_file):
    """Read the CSV, check router status, and update the file."""
    routers = []
    
    # Read CSV file
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ["Status"] if "Status" not in reader.fieldnames else reader.fieldnames
        for row in reader:
            ip = row["IP"]
            print(f"Pinging {ip} ({row['Name']})...")
            row["Status"] = "1" if ping_router(ip) else "0"
            routers.append(row)
            time.sleep(1)  # Avoid overwhelming the network

    # Write updated data back to CSV
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routers)
    
    print("CSV file updated successfully.")

# Example usage
csv_filename = "devices/routers.csv"  # Ensure this file exists with columns: Name, IP
check_routers(csv_filename)
