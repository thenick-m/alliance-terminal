import dearpygui.dearpygui as dpg
import time
import threading
from pygame import mixer
import random
import pyautogui
import json
from PIL import Image
import sys
import os

from modules import requesthandler4000 as rq

if hasattr(sys, '_MEIPASS'):  #pyinstaller
    BASE_DIR = sys._MEIPASS
elif getattr(sys, 'frozen', False):  #nuitka
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

METATEXT = "x4AllianceTerminal by thenick_m & willow"
VERSION = "0.0.1"

#init global vars
sfx_volume = 0.3
sfx = {}

#functions
def locally(relative_path):
    return os.path.join(BASE_DIR, relative_path)

def run_async(fn, callback):
    threading.Thread(target=lambda: callback(fn()), daemon=True).start()

def play_sound(filename, volume=1, max_time=None):
    global sfx

    if filename in sfx.keys():
        sound = sfx[filename]
    else:
        sfx[filename] = mixer.Sound(filename)
        sound = sfx[filename]


    sound.set_volume(volume)
    if max_time:
        sound.play(maxtime=max_time)
    else:
        sound.play()

    return sound

def retroify(image_path, tint=(250, 134, 55)):
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()  #preserve original alpha
    
    grayscale = Image.merge("RGB", (r, g, b)).convert("L")
    tinted = Image.new("RGB", img.size, tint)
    tinted = Image.blend(Image.new("RGB", img.size, (0,0,0)), tinted, 1.0)
    
    tinted = Image.composite(tinted, Image.new("RGB", img.size, (0,0,0)), grayscale)

    tinted.putalpha(a)
    return tinted

def load_pil_image(tag, img):
    img = img.convert("RGBA")
    width, height = img.size
    data = [x/255.0 for x in img.tobytes()]
    
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=tag)

#theme config
def set_theme(
    color1=(0, 0, 0),
    color2=(40, 20, 5),
    color3=(84, 41, 9),
    color4=(250, 134, 55)):
    with dpg.theme() as crt_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, color1)
            dpg.add_theme_color(dpg.mvThemeCol_Text, color4)
            dpg.add_theme_color(dpg.mvThemeCol_Border, color4)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, color2)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, color2)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, color3)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, color1)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, color1)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, color4)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, color2)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, color3)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, color2)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, color4)
            dpg.add_theme_color(dpg.mvThemeCol_Header, color3)
            dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, color4)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, color3)
            dpg.add_theme_color(dpg.mvThemeCol_Button, color2)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, color3)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, color4)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, color1)

    dpg.bind_theme(crt_theme)

#start gui
dpg.create_context()

#set theme
set_theme()

#start sound stuff
mixer.init()

#font config
with dpg.font_registry():
    with dpg.font(locally("other/fixedsys.ttf"), 14) as default_font:
        pass
dpg.bind_font(default_font)

# --- MAIN WINDOW ---
with dpg.window(label="x4at", tag="main_window"):
    
    with dpg.tab_bar():
        
        # --- SEARCH ---
        with dpg.tab(label="search", tag="search_tab"):
            fields = ["Hematite", 
                        "Malachite", 
                        "Gummite",
                        "Petroleum", 
                        "Coal", 
                        "Gold", 
                        "Sulfur", 
                        "Cerussite", 
                        "Lime", 
                        "Quartz", 
                        "Saltpeter", 
                        "Bauxite", 
                        "Tektite", 
                        "Tag",
                        "Life",
                        "Note",
                        "Oceans",
                        "Atmosphere",
                        "Tectonics",
                        "Moons",
                        "Name",
                        "Trees",
                        "StarID",
                        "PlanetID",
                        "Hardcoded",
                        "PlanetCount",
                        "Index",
                        "Radius",
                        "Gravity",
                        "Limestone",
                        "Saltground",
                        "Screenshots",
                        "SpectralType",
                        ]
            fields = [field.lower() for field in fields] #lower fields
            operators = ["==", "!=", ">", "<", ">=", "<=", "is", "are", "arent", "isnt", "over", "under", "has", "lacks"]
            field_values = {
                "atmosphere": ["terran", "martian", "venusian", "steam", "jovian", "titanean", "alkali", "silicate", "none"],
                "tectonics":["dunes", "ridges", "mountains", "continental", "chaos", "jovian"],
                "oceans": ["water", "acid", "air", "blood", "methane", "ammonia", "lava"],
                "trees":["poppy", "lepidodendron", "oak", "earthstar", "palm", "deathcap", "willow", "pine", "mold", "cherry"],
                "hardcoded": ["true", "false"],
                "lime": ["true", "false"],
                "life": ["true", "false"],
                "saltpeter": ["true", "false"],
                "limestone": ["true", "false"],
                "saltground": ["true", "false"],
                "screenshots":["true", "false"],
            }

            for field in fields: #add the rest of the fields
                if field in field_values.keys():
                    continue
                else:
                    field_values[field] = []


            for field, value in field_values.items(): #add present to everything
                if value == ["true", "false"]:
                    continue
                else:
                    value.append("present")
                    field_values[field] = value

            complete_conditions = []
            
            #get text suggestions for command line
            def get_suggestions(text):
                if text.endswith(" "): #stuff for making sure the autofill updates after enter is pressed
                    parts = text.strip().split(" ")
                    parts.append("")
                else:
                    parts = text.strip().split(" ")
                
                if len(parts) == 1:
                    return [f for f in fields if f.startswith(parts[0])]
                elif len(parts) == 2:
                    return [op for op in operators if op.startswith(parts[1])]
                elif len(parts) == 3:
                    field = parts[0]
                    return [v for v in field_values.get(field, []) if v.startswith(parts[2])]
                
                return []
            
            def on_input_change(sender, app_data):
                suggestions = get_suggestions(app_data)
                
                dpg.configure_item("suggestion_list", items=suggestions)

            def on_suggestion_click(sender, app_data):
                play_sound(locally("sounds/loading2.wav"), sfx_volume, max_time=100)

                #parse the query input
                current = dpg.get_value("query_input")
                if current.endswith(" "):
                    parts = current.strip().split(" ")
                    parts.append(app_data)
                else:
                    parts = current.strip().split(" ")
                    parts[-1] = app_data

                new_value = " ".join(parts)

                if len(parts) >= 3:
                    play_sound(locally("sounds/submit3.wav"), sfx_volume)
                    # submit and clear
                    complete_conditions.append(new_value)
                    dpg.configure_item("condition_list", items=complete_conditions)
                    dpg.set_value("query_input", "")
                    dpg.configure_item("suggestion_list", items=[])
                    dpg.focus_item("query_input")
                else:
                    dpg.set_value("query_input", new_value + " ")
                    dpg.focus_item("query_input")
                    # pyautogui in a thread, never sleep on main thread
                    threading.Timer(0.05, lambda: pyautogui.press("end")).start()

            def on_key_press(sender, app_data):
                if app_data == dpg.mvKey_Return:
                    text = dpg.get_value("query_input")
                    suggestions = get_suggestions(text)

                    if suggestions:
                        on_suggestion_click(None, suggestions[0])

                    #check if the condition is valid ok
                    query_input:str = dpg.get_value("query_input").strip()
                    if len(query_input.split(" ")) >= 3:
                        play_sound(locally("sounds/submit3.wav"), sfx_volume)

                        #submit and clear
                        complete_conditions.append(query_input)
                        dpg.configure_item("condition_list", items=complete_conditions)
                        dpg.set_value("query_input", "")
                        dpg.configure_item("suggestion_list", items=[])
                        dpg.focus_item("query_input")

            def on_key_release(sender, app_data):
                if dpg.is_item_focused("query_input"):
                    on_input_change(None, dpg.get_value("query_input"))

            def on_condition_click(sender, app_data):
                play_sound(locally("sounds/submit4.wav"), sfx_volume)

                #delete tjhat shit yk what im sayn 😂
                complete_conditions.pop(complete_conditions.index(app_data))
                dpg.configure_item("condition_list", items=complete_conditions)

            def submit_conditions(sender, app_data):
                play_sound(locally("sounds/submit5.wav"))

                if not complete_conditions:
                    return
                
                searchStringArg = " ".join([f"({condition})" for condition in complete_conditions])

                dpg.hide_item("condition_and_button")
                dpg.hide_item("query_input")
                dpg.hide_item("suggestion_list")
                dpg.show_item("loading_text")

                def populate_results(results):

                    play_sound(locally("sounds/reciept1.wav"), sfx_volume)
                    play_sound(locally("sounds/success.wav"), sfx_volume)

                    dpg.hide_item("loading_text")
                    dpg.show_item("results_panel")
                    dpg.show_item("back_button")
                    dpg.delete_item("results_panel", children_only=True)

                    #copied sorting code from x4a (i didn't want to rename too many vars so i just transferred the data from one to another)
                    matches = results
                    matches = [(tuple([int(id_num) for id_num in match[0].split("-")]), match[1]) for match in matches] #turn StarID into int tuple
                    matches = sorted(matches) #sort matches
                    matches = [("-".join([str(id_num) for id_num in match[0]]), match[1]) for match in matches] #turn int tuple into StarID
                    results = matches

                    for i, result in enumerate(results):
                        with dpg.child_window(parent="results_panel", width=-1, height=240, border=True, tag=f"result_{i}"):
                            dpg.add_text(f"{result[0]}\n\n{json.dumps(result[1], indent=4)}") #temporary until i figure out how histograms work here
                
                loading_text = ""
                def add_text_to_shit(text):
                    nonlocal loading_text
                    loading_text = f"{loading_text}\n{text}"
                    dpg.set_value("loading_text", loading_text)

                def do_search():
                    loading_sound = play_sound(locally("sounds/loading2.wav"), sfx_volume)
                    while not done[0]:
                        dpg.set_value("loading_text", f"POLLING... {["/", "-", "\\", "|"][int((time.perf_counter()*4)%4)]}")
                        time.sleep(0.1)
                    loading_sound.stop()

                done = [False]

                def on_complete(result):
                    done[0] = True

                    try:
                        populate_results(result['matches'])
                    except KeyError as e:
                        print(e)
                        play_sound(locally("sounds/error.wav"), sfx_volume)
                        play_sound(locally("sounds/error2.wav"), sfx_volume)

                        add_text_to_shit("ERROR: No matches found")
                        dpg.show_item("back_button")
                    except TypeError as e:
                        print(e)
                        play_sound(locally("sounds/error.wav"), sfx_volume)
                        play_sound(locally("sounds/error2.wav"), sfx_volume)

                        add_text_to_shit("ERROR: Couldn't contact server")
                        dpg.show_item("back_button")
                        

                threading.Thread(target=do_search, daemon=True).start()
                run_async(lambda: rq.search(searchStringArg), on_complete)

            def back_to_search(sender, app_data):
                play_sound(locally("sounds/submit4.wav"), sfx_volume)

                dpg.hide_item("loading_text")
                dpg.hide_item("results_panel")
                dpg.hide_item("back_button")
                dpg.show_item("condition_and_button")
                dpg.show_item("submit_button")
                dpg.show_item("query_input")
                dpg.show_item("suggestion_list")


            with dpg.handler_registry():
                dpg.add_key_release_handler(callback=on_key_release)
                dpg.add_key_press_handler(callback=on_key_press)
                dpg.add_mouse_wheel_handler(callback=lambda sender, app_data: play_sound(locally("sounds/scroll.wav"), sfx_volume, max_time=50))

            #UI
            with dpg.group(parent="search_tab"):
                
                dpg.add_text(tag="loading_text")
                dpg.hide_item("loading_text")

                with dpg.child_window(tag="results_panel", width=400, height=250, border=True):
                    dpg.hide_item("results_panel")

                dpg.add_button(label="back", tag="back_button",
                               callback=back_to_search,
                               width=400,
                               height=20)
                dpg.hide_item("back_button")

                with dpg.group(horizontal=True, tag="condition_and_button"):
                    dpg.add_listbox([], tag="condition_list",
                                    callback=on_condition_click,
                                    width=400, num_items=9)
                    
                    dpg.add_button(label="submit", tag="submit_button",
                                   callback=submit_conditions,
                                   width=150,
                                   height=170)

                dpg.add_input_text(tag="query_input", #query
                                hint="<field> <operator> <value>",
                                callback=on_input_change,
                                on_enter=True,
                                width=400)
                
                dpg.add_listbox([], tag="suggestion_list", #autofill
                                callback=on_suggestion_click,
                                width=150)
                                
                    
        # --- GET --- 
        with dpg.tab(label="get"):
            dpg.add_text("TBA")
        
        # --- EDIT ---
        with dpg.tab(label="edit"):
            dpg.add_text("TBA")

#startup sequence
with dpg.window(tag="startup_window"):

    #load text
    dpg.add_text("", tag="boot_text", wrap=600)

    #load image
    load_pil_image("logo", retroify(locally("other/logo.png")).resize((200, 200)))
    dpg.add_image("logo", pos=(420, 10))

def boot_sequence():
    def end_boot_sequence():
        dpg.hide_item("startup_window")
        dpg.show_item("main_window")
        dpg.set_primary_window("main_window", True)
        play_sound(locally("sounds/beep1.wav"), sfx_volume)

    boot_text = ""
    def add_boot_text(text):
        nonlocal boot_text
        boot_text += f"{text}\n"

        time.sleep(random.uniform(0.05, 0.2))
        dpg.set_value("boot_text", boot_text)

    border_string_length = 30
    def add_boot_border(title=""):
        border_thing = "-"*int((border_string_length-len(title)-(2 if title else 0))/2) #Hi
        add_boot_text(f"{border_thing}{f" {title} " if title else ""}{border_thing}")
        
    play_sound(locally("sounds/startup.wav"), 0.3)
    add_boot_text(METATEXT)
    add_boot_text(f"v{VERSION}")

    #settings stuff
    add_boot_border("LOADING SETTINGS")
    with open(locally('other/settings.json'), 'r', encoding='utf-8') as file:
        settings = json.load(file)

    #sfx volume
    global sfx_volume; sfx_volume = settings["sfx_volume"]; add_boot_text(f"sfx_volume: {sfx_volume}")

    #theme colors
    color1 = tuple(settings["color1"])
    color2 = tuple(settings["color2"])
    color3 = tuple(settings["color3"])
    color4 = tuple(settings["color4"])
    set_theme(color1, color2, color3, color4)

    #debug shit
    if settings["debug_mode"]: end_boot_sequence(); return

    #server connection stuff
    add_boot_border(f"SERVER CONNECTION")

    add_boot_text("trying server connection...")
    start_time = time.perf_counter()
    ping = rq.ping()
    if ping == None:
        add_boot_text("server connection failed")
        add_boot_text("attempt 2...")
        start_time = time.perf_counter()
        
    ping = rq.ping()
    if ping == None:
        add_boot_text("server connection failed")
        add_boot_text("closing program...")
        time.sleep(1)
        dpg.stop_dearpygui()

    ping_elapsed = time.perf_counter()-start_time

    add_boot_text(f"X4atbackend: {ping}")
    add_boot_text(f"ping: {1000*ping_elapsed:.2f}ms")
    add_boot_text("sever connection verified")

    add_boot_border()

    add_boot_text("starting main window...")
    time.sleep(0.1)
    
    time.sleep(settings["boot_up_time_hang"])
    end_boot_sequence()
    

dpg.create_viewport(title="x4AllianceTerminal", small_icon=locally("other/logo.ico"), large_icon=locally("other/logo.ico"), width=640, height=360, always_on_top=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("startup_window", True)

dpg.hide_item("main_window")
threading.Thread(target=boot_sequence, daemon=True).start()

dpg.start_dearpygui()
dpg.destroy_context()