import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))

def load_json_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def load_team_name_mapping() -> dict:
    try:
        filepath = os.path.join(current_dir, 'team_names_mapping.json')
        return load_json_file(filepath)
    except FileNotFoundError:
        print(f"Warning: team_names_mapping.json not found.")
        return {}


def load_team_ids_mapping() -> dict:
    try:
        filepath = os.path.join(current_dir, 'team_ids_mapping.json')
        return load_json_file(filepath)
    except FileNotFoundError:
        print(f"Warning: team_ids_mapping.json not found.")
        return {}
