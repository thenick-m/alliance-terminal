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

WIDTH = 363
HEIGHT = 705

debug = True

#init global vars
sfx_volume = 0.3
sfx = {}

color1 = (0, 0, 0)
color2 = (40, 20, 5)
color3 = (84, 41, 9)
color4 = (250, 134, 55)

search_results_view = False
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

def switch_search_view(sender, app_data):
    global search_results_view

    if search_results_view:
        play_sound(locally("sounds/submit4.wav"), sfx_volume)

        dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

        search_results_view = False
        dpg.hide_item("loading_text")
        dpg.hide_item("results_panel")
        dpg.hide_item("back_button")
        dpg.show_item("condition_and_button")
        dpg.show_item("submit_button")
        dpg.show_item("query_input")
        dpg.show_item("suggestion_list")
    else:
        dpg.configure_viewport(0, height=HEIGHT)
        search_results_view = True
        dpg.hide_item("condition_and_button")
        dpg.hide_item("query_input")
        dpg.hide_item("suggestion_list")
        dpg.show_item("loading_text")


#theme config
def make_theme(color1, color2, color3, color4):
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
            dpg.add_theme_color(dpg.mvPlotCol_Fill, color4, category=dpg.mvThemeCat_Plots)
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, color2+(100,))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, color2)
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
    return crt_theme

def set_theme(
    color1_set=(0, 0, 0),
    color2_set=(40, 20, 5),
    color3_set=(84, 41, 9),
    color4_set=(250, 134, 55)):

    global color1; color1 = color1_set
    global color2; color2 = color2_set
    global color3; color3 = color3_set
    global color4; color4 = color4_set

    crt_theme = make_theme(color1_set, color2_set, color3_set, color4_set)

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
    def on_tab_switch(sender, app_data):
        play_sound(locally("sounds/click.wav"))

        tab = tab = dpg.get_item_alias(app_data)

        if tab == "search_tab":
            if search_results_view:
                dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)
            else:
                dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

        elif tab == "get_tab":
            dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)
        elif tab == "settings_tab":
            dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

    
    with dpg.tab_bar(tag="tab_bar", callback=on_tab_switch):
        
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

            def submit_conditions(sender, app_data): #TODO: move this shit into another module
                global search_results_view

                play_sound(locally("sounds/submit5.wav"), sfx_volume)

                if not complete_conditions:
                    return
                
                searchStringArg = " ".join([f"({condition})" for condition in complete_conditions])
                print(complete_conditions)

                switch_search_view(0, 0)

                def populate_results(results):

                    def pretty_results_from_dict(results_dict):
                        return "\n".join([f"{key}: {value}" for key, value in results_dict.items()])

                    play_sound(locally("sounds/reciept1.wav"), sfx_volume)
                    play_sound(locally("sounds/success.wav"), sfx_volume)

                    dpg.set_value("loading_text", f"{len(results)} results {'(MAX)' if len(results) == 100 else ''}")
                    dpg.show_item("results_panel")
                    dpg.show_item("back_button")
                    dpg.delete_item("results_panel", children_only=True)

                    #dict of matches
                    results_dict = {result[0]: result[1] for result in results}

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

                        def change_get_planet(sender, app_data):
                            global current_get_planet

                            current_get_planet = results_dict[sender]

                            play_sound(locally("sounds/click2.wav"))
                            populate_get_tab(current_get_planet)
                            dpg.set_value("tab_bar", "get_tab")

                        dpg.add_button(label="get", width=80, height=300, tag=f"{result[0]}", parent=child, pos=(210, 10),
                                       callback=change_get_planet)

                def do_search():
                    loading_sound = play_sound(locally("sounds/loading2.wav"), sfx_volume)
                    while not done[0]:
                        dpg.set_value("loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
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

            with dpg.handler_registry():
                dpg.add_key_release_handler(callback=on_key_release)
                dpg.add_key_press_handler(callback=on_key_press)
                dpg.add_mouse_wheel_handler(callback=lambda sender, app_data: play_sound(locally("sounds/scroll.wav"), sfx_volume, max_time=50))

            #UI
            with dpg.group(parent="search_tab"):

                def go_through_quit(sender, app_data):
                    play_sound(locally("sounds/loading1.wav"))

                    boot_text = ""
                    def add_boot_text(text):
                        nonlocal boot_text
                        boot_text += f"{text}\n"

                        time.sleep(random.uniform(0.05, 0.2))
                        dpg.set_value("boot_text", boot_text)

                    dpg.hide_item("main_window")
                    dpg.show_item("startup_window")
                    dpg.set_value("boot_text", "")

                    #actually do stuff

                    add_boot_text("saving settings...")
                    
                    try:
                        with open(locally('other/settings.json'), 'w', encoding='utf-8') as file:
                            settings = {}
                            settings["color1"] = color1
                            settings["color2"] = color2
                            settings["color3"] = color3
                            settings["color4"] = color4
                            settings["sfx_volume"] = sfx_volume

                            json.dump(settings, file, indent=4) #saveshit
                    except Exception as e:
                        add_boot_text(f"ERROR: {e}")

                    add_boot_text("shutting down program...")
                    time.sleep(0.5)
                    dpg.stop_dearpygui()
                    

                dpg.add_button(tag="quit_button", label="quit", pos=(280, 10),
                               callback=go_through_quit)
                
                dpg.add_text(tag="loading_text")
                dpg.hide_item("loading_text")

                with dpg.child_window(tag="results_panel", width=-1, height=570, border=True):
                    dpg.hide_item("results_panel")

                dpg.add_button(label="back", tag="back_button",
                               callback=switch_search_view,
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
            with dpg.child_window(tag="get_tab_content", width=-1, height=590, border=False):
                pass

            dpg.add_button(label="back", width=-1, height=20)

        def populate_get_tab(planet): #TODO: move this shit into another module
            
            dpg.delete_item("get_tab_content", children_only=True)
            

            if not planet:
                dpg.add_text("No planet selected", parent="get_tab_content")
                return

            #separate data
            name = planet.get("Name", "No Name")
            star_id = planet.get("StarID", "None")
            index = planet.get("Index", "None")
            planet_id = planet.get("PlanetID", "None")
            planet_count = planet.get("PlanetCount", "None")

            physical = {
                "Gravity": planet.get("Gravity"),
                "Radius": planet.get("Radius"),
                "Moons": planet.get("Moons"),
            }

            environment = {
                "Atmosphere": planet.get("Atmosphere"),
                "Oceans": planet.get("Oceans"),
                "Tectonics": planet.get("Tectonics"),
                "Life": planet.get("Life"),
            }

            resource_fields_normalized = [f.lower() for f in resource_fields]

            deposit_fields = ["Lime", "Quartz", "Saltpeter", "Limestone", "Saltground", "Trees", "Quartz"]

            deposit_resources = {k: v for k, v in planet.items() if k in deposit_fields}

            numeric_resources = {k: v for k, v in planet.items() 
                                if k.lower() in resource_fields_normalized and not isinstance(v, bool)}
            

            # --- HEADER ---
            dpg.add_text(f"{name}", tag="planet_name_header", parent="get_tab_content")
            dpg.bind_item_font("planet_name_header", big_font)
            dpg.add_text(f"Star {star_id}  |  Planet {planet_id}/{planet_count}  |  Index {index}", 
                        parent="get_tab_content")
            dpg.add_separator(parent="get_tab_content")

            #physical stats list
            stats_graph = dpg.add_child_window(parent="get_tab_content", width=-1, height=200, border=True)
            dpg.add_text("[ PHYSICAL ]", parent=stats_graph)
            dpg.add_separator(parent=stats_graph)
            for key, val in physical.items():
                if val is not None:
                    dpg.add_text(f"{key:<10} {val}", parent=stats_graph)

            dpg.add_text("", parent=stats_graph)
            dpg.add_text("[ ENVIRONMENT ]", parent=stats_graph)
            dpg.add_separator(parent=stats_graph)
            for key, val in environment.items():
                if val is not None:
                    display = str(val).lower() if isinstance(val, bool) else val
                    dpg.add_text(f"{key:<10} {display}", parent=stats_graph)

            dpg.add_separator(parent="get_tab_content")

            #numeric resources bar chart
            
            resource_graph = dpg.add_child_window(parent="get_tab_content", width=-1, height=230, border=True)

            # header with toggle button
            header_group = dpg.add_group(horizontal=True, parent=resource_graph)
            dpg.add_text("[ RESOURCES ]", parent=header_group)
            dpg.add_button(label="text", tag="resource_toggle", parent=header_group, width=-1,
                        callback=lambda: toggle_resource_view(numeric_resources))
            
            dpg.add_separator(parent=resource_graph)

            resource_view = ["graph"]  #list so it's mutable from nested function

            def toggle_resource_view(numeric_resources):
                if resource_view[0] == "graph":
                    resource_view[0] = "text"
                    dpg.set_item_label("resource_toggle", "graph")
                    dpg.hide_item("resource_plot_container")
                    dpg.show_item("resource_text_container")
                    dpg.hide_item("get_legend")
                else:
                    resource_view[0] = "graph"
                    dpg.set_item_label("resource_toggle", "text")
                    dpg.show_item("resource_plot_container")
                    dpg.hide_item("resource_text_container")
                    dpg.show_item("get_legend")

            resource_plot_container = dpg.add_group(parent=resource_graph, tag="resource_plot_container")
            if numeric_resources:
                plot = dpg.add_plot(height=150, width=-1, parent=resource_plot_container,
                                no_menus=True, no_box_select=True, no_mouse_pos=True, no_inputs=True)
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, parent=plot, tag="get_x_axis", no_gridlines=True)
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, parent=plot, tag="get_y_axis", no_gridlines=True)

                present_fields = []
                known_fields = []
                present_x = []
                known_x = []
                present_y = []
                known_y = []

                all_fields = list(numeric_resources.keys())
                for j, (key, val) in enumerate(numeric_resources.items()):
                    if val == "Present" or val == "present":
                        present_fields.append(key)
                        present_x.append(float(j))
                        present_y.append(1.0)
                    else:
                        known_fields.append(key)
                        known_x.append(float(j))
                        known_y.append(float(val))

                if known_x:
                    dpg.add_bar_series(x=known_x, y=known_y, weight=0.7,
                                    label="Known", parent=y_axis)

                if present_x:
                    series = dpg.add_bar_series(x=present_x, y=present_y, weight=0.7,
                                            label="Present", parent=y_axis)
                    with dpg.theme() as present_theme:
                        with dpg.theme_component(dpg.mvBarSeries):
                            dpg.add_theme_color(dpg.mvPlotCol_Fill,
                                            color4+(100,),
                                            category=dpg.mvThemeCat_Plots)
                    dpg.bind_item_theme(series, present_theme)

                #shorten fields
                for i in range(len(all_fields)):
                    all_fields[i] = f"{all_fields[i][:4]}."

                dpg.set_axis_ticks("get_x_axis", 
                                tuple(zip(all_fields, [float(j) for j in range(len(all_fields))])))
                dpg.set_axis_limits("get_x_axis", -0.5, len(all_fields) - 0.5)
                dpg.fit_axis_data("get_y_axis")
                legend_group = dpg.add_group(horizontal=True, parent=resource_graph)
                dpg.add_text("[half-shaded] = Unknown\n[fully-shaded] = Known", parent=legend_group, tag="get_legend")
            else:
                    dpg.add_text(f"No resources logged", parent=resource_plot_container)

            #text container
            resource_text_container = dpg.add_group(parent=resource_graph, tag="resource_text_container", show=False)
            if numeric_resources:
                for key, val in numeric_resources.items():
                    display = "present" if val in ["Present", "present"] else str(val)
                    dpg.add_text(f"{key:<12} {display}", parent=resource_text_container)
            else:
                    dpg.add_text(f"No resources logged", parent=resource_text_container)

            #deposits
            dpg.add_separator(parent="get_tab_content")
            deposit_container = dpg.add_child_window(parent="get_tab_content", height=60)
            dpg.add_text("[ DEPOSITS ]", parent=deposit_container)
            bool_group = dpg.add_group(parent=deposit_container)
            if deposit_resources:
                dpg.add_text("".join([f"{key}, " for key in deposit_resources.keys()]), parent=bool_group)
            else:
                dpg.add_text(f"None", parent=bool_group)

        # --- EDIT ---
        with dpg.tab(label="edit", tag="edit_tab"):
            dpg.add_text("TBA")

        # --- SETTINGS --- 
        with dpg.tab(label="settings", tag="settings_tab"):

            def change_volume(app_data, sender):
                global sfx_volume

                play_sound(locally("sounds/scroll.wav"), sfx_volume, max_time=50)

                sfx_volume = sender

            dpg.add_slider_float(
                label="sfx volume",
                default_value=1,
                min_value=0,
                max_value=1,
                callback=change_volume
                )
            
            dpg.add_separator()
            with dpg.child_window(horizontal_scrollbar=True, width=-1, height=100):
                dpg.add_text("[ THEMES ]")
                with dpg.group(horizontal=True):
                    class ColorProfile:
                        def __init__(self, name, color1, color2, color3, color4):
                            self.name = name
                            self.color1 = color1
                            self.color2 = color2
                            self.color3 = color3
                            self.color4 = color4
                            self.theme = make_theme(color1, color2, color3, color4)

                        def change_theme(self):
                            play_sound(locally("sounds/click.wav"))
                            set_theme(self.color1, self.color2, self.color3, self.color4)

                        def add(self):
                            button = dpg.add_button(label=self.name, width=100, height=-1, callback=lambda sender, app_data: self.change_theme())
                            dpg.bind_item_theme(button, self.theme)


                    ColorProfile("phosphor", (0, 0, 0), (40, 20, 5), (84, 41, 9), (250, 134, 55)).add()
                    ColorProfile("byte", (20, 35, 29), (85, 101, 81), (150, 167, 134), (215, 233, 186)).add()

            dpg.add_separator()
            
            def sales_demolition(sender, app_data):
                play_sound(locally("sounds/click2.wav"))
                with dpg.window(label="kys bro", modal=True, no_close=True,
                                no_resize=True, no_move=True,
                                tag="thinking_window",
                                pos=(WIDTH//2 - 80, WIDTH//2 - 30)):
                    dpg.add_text("thinking...", tag="thinking_text")

                def bro_thinking():
                    while True:
                        dots = "." * (int(time.perf_counter() * 2) % 4)
                        dpg.set_value("thinking_text", f"thinking{dots}")
                        time.sleep(0.1)

                threading.Thread(target=bro_thinking, daemon=True).start()

            dpg.add_button(label="recompute base encryption hash key", callback=sales_demolition)

# --- startup sequence --- 
with dpg.window(tag="startup_window"):

    #load text
    dpg.add_text("", tag="boot_text", wrap=600)

    #load image
    load_pil_image("logo_texture", retroify(locally("other/logo.png")).resize((50, 50)))
    dpg.add_image("logo_texture", pos=(270, 250), tag="logo_image")

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
    try:
        with open(locally('other/settings.json'), 'r', encoding='utf-8') as file:
            settings = json.load(file)
    except json.decoder.JSONDecodeError:
        add_boot_text("ERROR: settings file corrupted")
        add_boot_text("loading with default settings...")

        settings = {
            "color1": [0, 0, 0],
            "color2": [40, 20, 5],
            "color3": [84, 41, 9],
            "color4": [250, 134, 55],
            "sfx_volume": 1,
                }

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
    
    load_pil_image("logo_texture", retroify(locally("other/logo.png"), color4).resize((50, 50)))

    dpg.add_image("logo_texture", pos=(270, 250), tag="logo_image", parent="startup_window")

    #debug shit
    if debug: end_boot_sequence(); return

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
    
    time.sleep(0.5)
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