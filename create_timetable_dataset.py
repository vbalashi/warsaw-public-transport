import os
import json
import csv
import glob

def adjust_time(time_str):
    """
    Adjusts time given as "HH:MM:SS". If hour >= 24, subtract 24 until hour is less than 24.
    Returns a formatted time string with two-digit hours.
    """
    parts = time_str.split(":")
    hour = int(parts[0])
    minute = parts[1]
    second = parts[2]
    while hour >= 24:
        hour -= 24
    return f"{hour:02d}:{minute}:{second}"

# Folder where the timetable files are located
folder = "data/timetable/"
# Use glob to get all JSON files in the folder
filepaths = glob.glob(os.path.join(folder, "*.json"))

# Prepare a list to store our timetable rows
timetable = []

for filepath in filepaths:
    filename = os.path.basename(filepath)
    # Remove the .json extension and split on underscore to get route, group, platform
    parts = filename[:-5].split("_")
    if len(parts) != 3:
        # Skip files that do not match the expected filename pattern
        continue
    route, bus_stop_group, bus_stop_platform = parts
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        continue

    # Check that data contains the key "result"
    if not isinstance(data, dict) or "result" not in data:
        # Skip or log error for files that don't have the expected structure
        print(f"Skipping {filename}: 'result' key not found")
        continue
        
    # Skip if result is not a list or is a string message like "Błędna metoda lub parametry wywołania" or "null"
    if not isinstance(data["result"], list):
        print(f"Skipping {filename}: 'result' is not a list (value: {data['result']})")
        continue

    # Process each record in the "result" list
    for record in data["result"]:
        # Skip if record is not a list of dictionaries
        if not isinstance(record, list):
            continue
            
        next_bus_stop = None
        time_value = None
        
        for item in record:
            if not isinstance(item, dict):
                continue
                
            if item.get("key") == "kierunek":
                next_bus_stop = item.get("value")
            elif item.get("key") == "czas":
                # Adjust the time if needed
                time_raw = item.get("value")
                if time_raw:
                    time_value = adjust_time(time_raw)
        # Only add a row if both next_bus_stop and time_value were found
        if next_bus_stop is not None and time_value is not None:
            timetable.append([route, bus_stop_group, bus_stop_platform, next_bus_stop, time_value])

# df_bus_timetable = pd.DataFrame(timetable)

# Write the timetable to a CSV file
output_csv = "timetable_timetable.csv"
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["route", "bus_stop_group", "bus_stop_platform", "next_bus_stop", "time"])
    writer.writerows(timetable)

print(f"timetable created with {len(timetable)} rows and saved as {output_csv}")
