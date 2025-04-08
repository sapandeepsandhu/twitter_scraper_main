import yaml
from datetime import datetime

SETTINGS_FILE = "settings.yaml"

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def load_yaml(file_path):
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return data
    except yaml.YAMLError as e:
        print("❌ YAML parsing error:")
        print(e)
        return None

def check_and_fix_yaml(data, fix_dates=False, new_since=None, new_until=None):
    if "query_list" not in data:
        print("❌ 'query_list' not found in settings.yaml")
        return

    seen_handles = set()
    fixed_query_list = []
    duplicates = []

    for i, q in enumerate(data["query_list"]):
        if "handle" not in q:
            print(f"❌ Entry {i} missing 'handle': {q}")
            continue

        handle = q["handle"]

        # Check for duplicates
        if handle in seen_handles:
            print(f"⚠️ Duplicate found: {handle}")
            duplicates.append(handle)
            continue
        seen_handles.add(handle)

        # Validate and fix dates if requested
        if fix_dates:
            q["since"] = new_since
            q["until"] = new_until
        else:
            if not is_valid_date(q.get("since", "")):
                print(f"❌ Invalid 'since' date for {handle}: {q.get('since')}")
            if not is_valid_date(q.get("until", "")):
                print(f"❌ Invalid 'until' date for {handle}: {q.get('until')}")

        fixed_query_list.append(q)

    # Update and save
    data["query_list"] = fixed_query_list
    with open(SETTINGS_FILE, "w") as f:
        yaml.dump(data, f, sort_keys=False)

    print("✅ YAML validation complete.")
    if fix_dates:
        print(f"📅 All dates updated to: since = {new_since}, until = {new_until}")
    if duplicates:
        print(f"🔁 Removed duplicates: {duplicates}")

def main():
    data = load_yaml(SETTINGS_FILE)
    if data:
        # Option: change this to True to update all dates
        fix_all_dates = True
        new_since = "2023-01-01"
        new_until = "2025-01-01"
        check_and_fix_yaml(data, fix_dates=fix_all_dates, new_since=new_since, new_until=new_until)

if __name__ == "__main__":
    main()
