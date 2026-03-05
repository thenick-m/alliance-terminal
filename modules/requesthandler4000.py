#requesthandler4000.py
import requests
import uuid
import time

BASE_URL = "https://x4alliancebackend-default-rtdb.firebaseio.com"
polls = 5

def request(command:str="", args:dict={}):
    req_id = str(uuid.uuid4()) #id used to identify request

    print(f"sending {command} request with id: {req_id}")

    requests.put(f"{BASE_URL}/requests/{req_id}.json", json={
        "command": command,
        "args": args,
        "ip": "test",
        "status": "pending"
    })

    print(f"beginning polling for: {req_id}")

    for _ in range(polls): #how many times to poll
        r = requests.get(f"{BASE_URL}/responses/{req_id}.json")
        if r.json():
            return r.json()
        time.sleep(0.5)
    else:
        print(f"timed out")
        return None

def ping():
    return request("ping")

def search(stringSearchArg:str):
    return request("search", {"stringSearchArg": stringSearchArg})

def get(planetID:str):
    return request("get", {"planetID": planetID})

def count(stringSearchArg:str):
    return request()

#print(search("(malachite = present)")) #testing