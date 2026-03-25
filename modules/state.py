#global manager
#DO NOT MOVE FROM MODULES FOLDER OR THE locally FUNCTION WILL NOT WORK PROPERLY

import sys
import os
import threading
import json

#base_dir init
if hasattr(sys, '_MEIPASS'):  #pyinstaller
    BASE_DIR = sys._MEIPASS
elif getattr(sys, 'frozen', False):  #nuitka
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- functions ---

def locally(relative_path): #local filepath (used for accessing relative files)
    return os.path.join(BASE_DIR, relative_path)

def savepath(relative_path):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)  #create dirs if missing
    return path

def run_async(fn, callback):
    threading.Thread(target=lambda: callback(fn()), daemon=True).start()

# --- global vars ---

WIDTH = 363
HEIGHT = 705

debug = False

color1 = (0, 0, 0)
color2 = (40, 20, 5)
color3 = (84, 41, 9)
color4 = (250, 134, 55)

noise = True

search_results_view = False
current_get_planet = None
current_edit_planet = None; current_edit_index = None

big_font = None #INITIALIZE INSIDE OF MAIN!!!!!!!

with open(locally("other/fields.json"), "r") as f:
    field_data = json.load(f)