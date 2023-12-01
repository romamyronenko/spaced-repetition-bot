import requests


def get_url():
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    return response.json()["tunnels"][0]["public_url"]
