import os
import yaml
import shutil

# === CONFIGURATION ===
# Input file with new Twitter handles (one per line)
input_file = "/Users/sapandeepsinghsandhu/Desktop/usernamesbatch2.txt"

# Settings YAML file that the scraper uses
settings_file = "/Users/sapandeepsinghsandhu/Desktop/twitter_scraper_main/settings.yaml"

# File to store (or archive) already processed handles
processed_file = "/Users/sapandeepsinghsandhu/Desktop/twitter_scraper_main/scrapped_3.txt"

# Date ranges (modify if needed)
since_date = "2023-01-01"
until_date = "2025-01-01"

# === PROCESS THE INPUT FILE ===

try:
    with open(input_file, "r") as f:
        twitter_handles = f.readlines()
except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found. Please check the file path.")
    exit(1)
except Exception as e:
    print(f"An error occurred while reading {input_file}: {e}")
    exit(1)

output_yaml = []  # Will store our YAML-structured list
processed_handles = []  # For archiving

for handle in twitter_handles:
    clean_handle = handle.strip().lstrip("@")
    if not clean_handle:
        continue
    entry = {
        "handle": clean_handle,
        "since": since_date,
        "until": until_date
    }
    output_yaml.append(entry)
    # Save the raw handle (with '@' removed) for moving to scrapped.txt later.
    processed_handles.append(clean_handle)

if not output_yaml:
    print("No valid Twitter handles found in the input file.")
    exit(0)

# === UPDATE THE SETTINGS YAML FILE ===
# We'll store our handles under a top-level key "query_list"
data = {"query_list": output_yaml}

try:
    with open(settings_file, "w") as f:
        # Use safe_dump with default_flow_style=False for pretty formatting
        yaml.safe_dump(data, f, default_flow_style=False)
    print(f"✅ Updated settings file: {settings_file}")
except Exception as e:
    print(f"Error writing to {settings_file}: {e}")
    exit(1)

# === ARCHIVE THE PROCESSED HANDLES ===
# We want to move processed handles into a separate file (scrapped.txt)
# If scrapped.txt already exists, we'll append; otherwise, we'll create it.
try:
    mode = "a" if os.path.exists(processed_file) else "w"
    with open(processed_file, mode) as pf:
        for handle in processed_handles:
            pf.write(handle + "\n")
    print(f"✅ Processed handles appended to {processed_file}")
except Exception as e:
    print(f"Error updating {processed_file}: {e}")

# === OPTIONAL: DELETE OR RENAME THE INPUT FILE ===
# If you prefer to remove the input file once processed (to avoid reprocessing):
try:
    os.remove(input_file)
    print(f"✅ Removed input file: {input_file}")
except Exception as e:
    print(f"Warning: could not remove {input_file}: {e}")
