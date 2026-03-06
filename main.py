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

WIDTH = 360
HEIGHT = 640

#init global vars
sfx_volume = 0.3
sfx = {}
current_get_planet = None

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
    with dpg.font(locally("other/fixedsys.ttf"), 25) as big_font:
        pass

dpg.bind_font(default_font)

# --- MAIN WINDOW ---
with dpg.window(label="x4at", tag="main_window"):
    
    with dpg.tab_bar(tag="tab_bar", callback=lambda: play_sound(locally("sounds/click.wav"))):
        
        # --- SEARCH ---
        with dpg.tab(label="search", tag="search_tab"):
            with open(locally("other/fields.json"), "r") as f:
                field_data = json.load(f)

            operators = field_data["operators"]
            field_values = {k.lower(): v for k, v in field_data["fields"].items()}
            fields = list(field_values.keys())
            resource_fields = field_data["resource_fields"]

            #add present to non-boolean fields
            for field, values in field_values.items():
                if values != ["true", "false"] and values != [] and "present" not in values:
                    values.append("present")

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
                    #submit and clear
                    complete_conditions.append(new_value)
                    dpg.configure_item("condition_list", items=complete_conditions)
                    dpg.set_value("query_input", "")
                    dpg.configure_item("suggestion_list", items=[])
                    dpg.focus_item("query_input")
                else:
                    dpg.set_value("query_input", new_value + " ")
                    dpg.focus_item("query_input")

                    #this is a hack to get around highlighting
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

            def on_get_click(sender, app_data):
                global current_get_planet
                current_get_planet = sender[:-4]

                play_sound(locally("sounds/click2.wav"))
                dpg.set_value("tab_bar", "get_tab")

            def submit_conditions(sender, app_data):
                play_sound(locally("sounds/submit5.wav"))

                if not complete_conditions:
                    return
                
                dpg.configure_viewport(0, height=700)
                
                searchStringArg = " ".join([f"({condition})" for condition in complete_conditions])
                print(complete_conditions)

                dpg.hide_item("condition_and_button")
                dpg.hide_item("query_input")
                dpg.hide_item("suggestion_list")
                dpg.show_item("loading_text")

                def populate_results(results):

                    def pretty_results_from_dict(results_dict):
                        return "\n".join([f"{key}: {value}" for key, value in results_dict.items()])

                    play_sound(locally("sounds/reciept1.wav"), sfx_volume)
                    play_sound(locally("sounds/success.wav"), sfx_volume)

                    dpg.set_value("loading_text", f"{len(results)} results {"(MAX)" if len(results) == 100 else ""}")
                    dpg.show_item("results_panel")
                    dpg.show_item("back_button")
                    dpg.delete_item("results_panel", children_only=True)


                    #copied sorting code from x4a
                    results = [(tuple([int(id_num) for id_num in result[0].split("-")]), result[1]) for result in results] #turn StarID into int tuple
                    results = sorted(results) #sort matches
                    results = [("-".join([str(id_num) for id_num in result[0]]), result[1]) for result in results] #turn int tuple into StarID

                    for i, result in enumerate(results):
                        
                        #cleanse results for display
                        result_to_display = result[1].copy()
                        if "Name" in result_to_display:
                            del result_to_display["Name"]
                        for key in list(result_to_display.keys()):
                            if key in resource_fields:
                                del result_to_display[key]

                        resource_dict = {key: result[1][key] for key in result[1] if key in resource_fields}

                        child = dpg.add_child_window(parent="results_panel", width=300, height=400, border=True, tag=f"result_{i}")

                        dpg.add_text(
                            f"{result[0]} {result[1].get('Name', 'No Name')}",
                            parent=child,
                            wrap=180,
                            tag=f"{result[0]}_result_title"
                        )
                        dpg.bind_item_font(f"{result[0]}_result_title", big_font)

                        dpg.add_text(
                            f"\n{pretty_results_from_dict(result_to_display)}",
                            parent=child,
                            wrap=180
                        )

                        dpg.add_button(label="get", width=80, height=300, tag=f"{result[0]}_get", parent=child, pos=(210, 10),
                                       callback=on_get_click)

                def do_search():
                    loading_sound = play_sound(locally("sounds/loading2.wav"), sfx_volume)
                    while not done[0]:
                        dpg.set_value("loading_text", f"POLLING... {["/", "-", "\\", "|"][int((time.perf_counter()*4)%4)]}")
                        time.sleep(0.1)
                    loading_sound.stop()

                done = [False]

                def on_complete(result):
                    done[0] = True

                    def set_text(text):
                        dpg.set_value("loading_text", text)

                    if result == None:
                        set_text("ERROR: couldn't contact server")
                    elif 'error' in result.keys():
                        set_text(f"ERROR: {result['error']}")
                    else:
                        populate_results(result['matches'])
                        return
                    
                    play_sound(locally("sounds/error.wav"), sfx_volume)
                    play_sound(locally("sounds/error2.wav"), sfx_volume)
                    dpg.show_item("back_button")
                        

                threading.Thread(target=do_search, daemon=True).start()
                run_async(lambda: rq.search(searchStringArg), on_complete)

            def back_to_search(sender, app_data):
                play_sound(locally("sounds/submit4.wav"), sfx_volume)

                dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

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

                with dpg.child_window(tag="results_panel", width=-1, height=570, border=True):
                    dpg.hide_item("results_panel")

                dpg.add_button(label="back", tag="back_button",
                               callback=back_to_search,
                               width=-1,
                               height=20)
                dpg.hide_item("back_button")

                with dpg.group(horizontal=True, tag="condition_and_button"):
                    dpg.add_listbox([], tag="condition_list",
                                    callback=on_condition_click,
                                    width=200, num_items=9)
                    
                    dpg.add_button(label="submit", tag="submit_button",
                                   callback=submit_conditions,
                                   width=100,
                                   height=170)

                dpg.add_input_text(tag="query_input", #query
                                hint="<field> <operator> <value>",
                                callback=on_input_change,
                                on_enter=True,
                                width=200)
                
                dpg.add_listbox([], tag="suggestion_list", #autofill
                                callback=on_suggestion_click,
                                width=150)
                                
                    
        # --- GET --- 
        with dpg.tab(label="get", tag="get_tab"):
            dpg.add_text("TBA")
        
        # --- EDIT ---
        with dpg.tab(label="edit", tag="edit_tab"):
            dpg.add_text("TBA")

#startup sequence
with dpg.window(tag="startup_window"):

    #load text
    dpg.add_text("", tag="boot_text", wrap=600)

    #load image
    load_pil_image("logo_texture", retroify(locally("other/logo.png")).resize((200, 200)))
    dpg.add_image("logo_texture", pos=(420, 10), tag="logo_image")

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
    add_boot_text(f"color1: {color1}")
    add_boot_text(f"color2: {color2}")
    add_boot_text(f"color3: {color3}")
    add_boot_text(f"color4: {color4}")

    dpg.delete_item("logo_image")
    dpg.delete_item("logo_texture")
    
    load_pil_image("logo_texture", retroify(locally("other/logo.png"), color4).resize((200, 200)))

    dpg.add_image("logo_texture", pos=(420, 10), tag="logo_image", parent="startup_window")

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
    

dpg.create_viewport(title="x4AllianceTerminal", 
                    small_icon=locally("other/logo.ico"), 
                    large_icon=locally("other/logo.ico"), 
                    width=WIDTH, height=WIDTH,
                    x_pos=1500, 
                    always_on_top=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("startup_window", True)

dpg.hide_item("main_window")
threading.Thread(target=boot_sequence, daemon=True).start()

dpg.start_dearpygui()
dpg.destroy_context()