#requesthandler4000.py

from modules import discord_auth
from modules import state
import requests
import uuid
import time

#testing
#import discord_auth

BASE_URL = "https://x4alliancebackend-default-rtdb.firebaseio.com"
CLIENT_ID = str(uuid.uuid4()) #id used to identify user in current session
discord_token = None


def request(command:str="", args:dict={}, polls=5):
    req_id = str(uuid.uuid4()) #id used to identify request

    print(f"sending {command} request with id: {req_id}")

    payload = {
        "command": command,
        "args": args,
        "id": CLIENT_ID,
        "status": "pending" 
    }

    #editor auth
    if discord_token:
        payload["discord_token"] = discord_token

    requests.put(f"{BASE_URL}/requests/{req_id}.json", json=payload) #send it out

    print(f"beginning polling for: {req_id}")

    for _ in range(polls): #how many times to poll
        r = requests.get(f"{BASE_URL}/responses/{req_id}.json")
        if r.json():
            return r.json()
        time.sleep(0.5)
    else:
        print(f"timed out")
        return None
    
def editor_login():
    global discord_token
    code = discord_auth.login()
    if not code:
        print("login failed")
        return False
    
    #server exchanges the code and returns a token
    result = request("discord_login", {"code": code})
    if result["is_editor"]:
        discord_token = result["token"]

        state.editor_mode = True
        print("editor mode enabled")

    return result

def edit(stringSearchArg):
    return request("edit", {"stringSearchArg": stringSearchArg})

def ping():
    return request("ping")

def search(stringSearchArg:str):
    return request("search", {"stringSearchArg": stringSearchArg}, polls=10)

def get(planetID:str):
    return request("get", {"planetID": planetID}, polls=7)

def count(stringSearchArg:str):
    return request("count", {"stringSearchArg": stringSearchArg})

def leaderboard():
    return request("leaderboard", polls=10)