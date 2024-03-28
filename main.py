import requests
import sched
import time
from datetime import datetime, timedelta
import json

data = {}
DEV_OM2M_HEADER = "dev_guest:dev_guest"


def fetch_nodes_info_from_json(file_path):
    """
    Fetches nodes information from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.

    Raises:
        FileNotFoundError: If the JSON file is not found.
        Exception: If an error occurs while reading the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            content = json.load(file)
            return content
    except FileNotFoundError:
        print("Local JSON file not found.")
        return None
    except Exception as e:
        print(f"Error occurred while reading local JSON file: {e}")
        return None


def fetch_data_ts(channel_id, api_key):
    """
    Fetches the last data entry from a ThingSpeak channel.

    Args:
        channel_id (int): The ID of the ThingSpeak channel.
        api_key (str): The API key for accessing the channel.

    Returns:
        dict: The JSON response containing the last data entry from the channel.
    """
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds/last.json?api_key={api_key}"
    response = requests.get(url)
    if 200 <= response.status_code < 300:
        data = response.json()
        return data
    else:
        print(f"Error: HTTP {response.status_code}")
        return None


def post_om2m(node_id, node_data, onem2m_endpoint, headers):
    """
    Posts data to oneM2M server.

    Args:
        node_id (str): The ID of the node.
        node_data (dict): The data of the node.
        onem2m_endpoint (str): The endpoint URL of the oneM2M server.
        headers (dict): The headers to be included in the request.

    """
    timestamp_str = node_data.get("created_at", None)
    timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
    timestamp_dt += timedelta(hours=5, minutes=30)
    epoch_time = int(timestamp_dt.timestamp())
    print(f"New data fetched for node {node_id}: {node_data} at {epoch_time}")
    data_dict = {
        "epoch_time": epoch_time,
        "water_level": float(node_data["field6"]),
        "temp": float(node_data["field7"]),
    }
    values_list = list(data_dict.values())
    payload = {
        "m2m:cin": {
            "lbl": ["AE-WM-WL", node_id, "V1.0.0", "WM-WL-V1.0.0"],
            "con": json.dumps(values_list),
        }
    }
    response = requests.post(onem2m_endpoint, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Data posted to oneM2M for node {node_id}")
    else:
        print(f"Data not posted to oneM2M with code : {response.status_code}")


def fetch_and_update_data(node):
    """
    Fetches data from a ThingSpeak channel, updates the node data, and posts it to an OM2M endpoint.

    Args:
        node (dict): A dictionary containing information about the node.
    """
    channel_id = node["channel_id"]
    api_key = node["api_key"]
    last_entry_id = node.get("last_entry_id", None)

    data = fetch_data_ts(channel_id, api_key)
    new_entry_id = data.get("entry_id", None)

    if last_entry_id == new_entry_id:
        print(
            f"No new data for node {node['node_id']}. Reason: Already up to date (entry_id: {last_entry_id})"
        )
        return

    node_data = {"created_at": data.get("created_at", None), "entry_id": new_entry_id}

    for key in data:
        if key.startswith("field"):
            node_data[key] = data[key]

    data[node["node_id"]] = node_data
    node["last_entry_id"] = new_entry_id
    headers = {
        "X-M2M-Origin": DEV_OM2M_HEADER,
        "Content-Type": "application/json;ty=4",
    }
    post_om2m(node["node_id"], node_data, node["onem2m_endpoint"], headers)


def fetch_and_update_periodically(scheduler, nodes_info):
    """
    Fetches and updates data for each node in the given nodes_info list periodically.

    Args:
        scheduler: The scheduler object used to schedule the periodic execution.
        nodes_info: A list of nodes information.

    Returns:
        None
    """
    for node in nodes_info:
        fetch_and_update_data(node)
    scheduler.enter(600, 1, fetch_and_update_periodically, (scheduler, nodes_info))


file_path = "nodes_info.json"
nodes_info = fetch_nodes_info_from_json(file_path)

scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(0, 1, fetch_and_update_periodically, (scheduler, nodes_info))
scheduler.run()
