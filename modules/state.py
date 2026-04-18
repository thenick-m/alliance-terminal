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

WIDTH:int = 363
HEIGHT:int = 705

debug:bool = False

# --- settings ---

#themes
color1:tuple = (0, 0, 0)
color2:tuple = (40, 20, 5)
color3:tuple = (84, 41, 9)
color4:tuple = (250, 134, 55)


#search
search_results_view:bool = False


#edit
current_get_planet:bool = None

current_edit_planet:bool = None; current_edit_index = None


#screenshots
screenie_ids = None

#languages
lang = "en"

def load_lang(language):
    global lang
    lang = language
    try:
        with open(locally(f"other/lang/{language}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(locally("other/lang/en.json"), "r", encoding="utf-8") as f:
            return json.load(f)
        
strings = load_lang(lang)

def reload_strings():
    global strings
    strings = load_lang(lang)

def t(key):  #translate
    return strings.get(key, key)

#other
big_font = None #INITIALIZE INSIDE OF MAIN!!!!!!!

noise:bool = True

colorbars:bool = False

always_on_top = True

screenshake = True

with open(locally("other/fields.json"), "r") as f:
    field_data = json.load(f)

import numpy as np
from dearpygui import dearpygui as dpg
import time
def shake_viewport(intensity=8, duration=0.3, falloff=True):
    def _run():
        if screenshake:
            rng = np.random.default_rng()
            viewport_config = dpg.get_viewport_configuration("DPG NOTSET")
            x = viewport_config['x_pos']
            y = viewport_config['y_pos']
            t_start = time.perf_counter()

            while True:
                elapsed = time.perf_counter() - t_start
                t = elapsed / duration

                if t >= 1.0:
                    dpg.set_viewport_pos((x, y)) #snap back to origin
                    break

                strength = intensity * (1.0 - t) if falloff else intensity
                ox = int(rng.uniform(-strength, strength))
                oy = int(rng.uniform(-strength, strength))
                dpg.set_viewport_pos((x + ox, y + oy))

                time.sleep(0.016)

    threading.Thread(target=_run, daemon=True).start()