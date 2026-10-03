#requesthandler4000.py

from modules import discord_auth
from modules import state

import requests

BASE_URL = "https://x4alliance.duckdns.org/api"

discord_token = None


def _safe(fn):
    """Runs an HTTP call and returns None on any network failure, matching
    the old behavior where a timed-out poll also returned None -- so nothing
    in get.py/search.py/edit.py needs to change how it checks for failure."""
    try:
        return fn()
    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return None


def editor_login():
    global discord_token
    code = discord_auth.login()
    if not code:
        print("login failed")
        return False

    result = _safe(lambda: requests.get(f"{BASE_URL}/discord/login", params={"code": code}).json())
    if result and result.get("is_editor"):
        discord_token = result["token"]
        print("editor mode enabled")

    return result


def get_radio_state():
    return _safe(lambda: requests.get(f"{BASE_URL}/radio").json())


def get_screenie(planetid, pos):
    return _safe(lambda: requests.get(
        f"{BASE_URL}/screenshot", params={"planetID": planetid, "position": pos}
    ).json())


def edit(stringSearchArg):
    headers = {"Authorization": f"Bearer {discord_token}"} if discord_token else {}
    return _safe(lambda: requests.post(
        f"{BASE_URL}/edit", json={"stringSearchArg": stringSearchArg}, headers=headers
    ).json())


def ping():
    return _safe(lambda: requests.get(f"{BASE_URL}/ping").json())


def search(stringSearchArg: str):
    return _safe(lambda: requests.post(
        f"{BASE_URL}/search", json={"stringSearchArg": stringSearchArg}
    ).json())


def get(planetID: str):
    return _safe(lambda: requests.get(f"{BASE_URL}/get", params={"planetID": planetID}).json())


def count(stringSearchArg: str):
    return _safe(lambda: requests.post(
        f"{BASE_URL}/count", json={"stringSearchArg": stringSearchArg}
    ).json())


def leaderboard():
    return _safe(lambda: requests.get(f"{BASE_URL}/leaderboard").json())