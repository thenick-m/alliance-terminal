from dearpygui import dearpygui as dpg
import time
import threading
from pygame import mixer
import random
import json

from modules import requesthandler4000 as rq
from modules.state import *
from modules import state #reimport cached state module into namespace for redundancy
from modules import audioshit as sound
from modules import imagehelpers

METATEXT = "x4AllianceTerminal by thenick_m & willow"
VERSION = "0.1.0"

debug = True

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
            dpg.add_theme_color(dpg.mvThemeCol_Tab, color2)            
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, color2+(100,))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, color2)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, color3)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, color4)            
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
    color1_set=(10, 10, 10),
    color2_set=(40, 20, 5),
    color3_set=(84, 41, 9),
    color4_set=(250, 134, 55)
    ):

    state.color1 = color1_set
    state.color2 = color2_set
    state.color3 = color3_set
    state.color4 = color4_set
    imagehelpers.tint = color4_set

    crt_theme = make_theme(color1_set, color2_set, color3_set, color4_set)

    dpg.bind_theme(crt_theme)

# --- MAIN ---

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
        state.big_font = big_font

dpg.bind_font(default_font)

#texture config mainly for noise shit
with dpg.texture_registry():
    initial = imagehelpers.generate_noise(WIDTH, HEIGHT).convert("RGBA")
    data = [x/255.0 for x in initial.tobytes()]
    dpg.add_dynamic_texture(WIDTH, HEIGHT, data, tag="noise_texture")


# --- MAIN WINDOW ---
with dpg.window(label="x4at", tag="main_window"):

    def go_through_quit(sender, app_data):
        sound.play_sound(locally("sounds/loading1.wav"))

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
        
        with open(savepath('other/settings.json'), 'w', encoding='utf-8') as file:
            settings = {}
            settings["color1"] = state.color1
            settings["color2"] = state.color2
            settings["color3"] = state.color3
            settings["color4"] = state.color4
            settings["sfx_volume"] = sound.sfx_volume
            settings["noise"] = state.noise

            json.dump(settings, file, indent=4) #saveshit

        add_boot_text("shutting down program...")
        time.sleep(0.5)
        dpg.stop_dearpygui()

    dpg.add_button(tag="quit_button", label="quit", pos=(305, 5), callback=go_through_quit)

    def on_tab_switch(sender, app_data):
        sound.play_sound(locally("sounds/click.wav"))

        tab = dpg.get_item_alias(app_data) #this is supposed to unfuck it since dpg app_data sends as dpg id 

        if tab == "search_tab":
            if state.search_results_view:
                dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)
            else:
                dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

        elif tab == "get_tab":
            if state.current_get_planet:
                dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)
            else:
                dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

        elif tab == "settings_tab":
            dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

    
    with dpg.tab_bar(tag="tab_bar", callback=on_tab_switch):
        #modularized tabs into their own py file in v0.1.0

        # --- SEARCH ---
        with dpg.tab(label="search", tag="search_tab"):
            from tabs.search import search
            search()

        # --- GET --- 
        with dpg.tab(label="get", tag="get_tab"):
            from tabs.get import get
            get()            

        # --- EDIT ---
        with dpg.tab(label="edit", tag="edit_tab"):
            from tabs.edit import edit
            edit()

        # --- SETTINGS --- 
        with dpg.tab(label="settings", tag="settings_tab"):
            
            with dpg.child_window(horizontal_scrollbar=True, width=-1, height=150):
                dpg.add_text("[ THEMES ]")
                with dpg.group(horizontal=True):
                    class Theme:
                        def __init__(self, name, color1, color2, color3, color4):
                            self.name = name
                            self.color1 = color1
                            self.color2 = color2
                            self.color3 = color3
                            self.color4 = color4
                            self.theme = make_theme(color1, color2, color3, color4)

                        def change_theme(self):
                            sound.play_sound(locally("sounds/click2.wav"))
                            set_theme(self.color1, self.color2, self.color3, self.color4)

                        def add(self):
                            button = dpg.add_button(label=self.name, width=100, height=-1, callback=lambda sender, app_data: self.change_theme())
                            dpg.bind_item_theme(button, self.theme)


                    Theme("phosphor", (10, 10, 10), (40, 20, 5), (84, 41, 9), (250, 134, 55)).add()
                    Theme("byte", (20, 35, 29), (85, 101, 81), (150, 167, 134), (215, 233, 186)).add()
                    Theme("girly girl", (54, 42, 53), (112, 89, 110), (161, 127, 158), (255, 183, 197)).add()
                    Theme("manly man", (10, 10, 13), (75, 75, 94), (139, 139, 174), (204, 204, 255)).add()


            dpg.add_separator()

            def change_volume(sender, app_data):

                sound.play_sound(locally("sounds/scroll.wav"), max_time=50)

                sound.sfx_volume = app_data

            dpg.add_slider_float(
                label="sfx volume",
                default_value=1,
                min_value=0,
                max_value=1,
                callback=change_volume
                )
            
            def toggle_noise(sender, app_data):
                state.noise = not state.noise

            dpg.add_separator()

            dpg.add_checkbox(label="noise", callback=toggle_noise, default_value=state.noise)
            
            def sales_demolition(sender, app_data):
                sound.play_sound(locally("sounds/click2.wav"))
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

            dpg.add_separator()

            dpg.add_button(label="recompute base encryption hash key", callback=sales_demolition)

# --- startup sequence --- 
with dpg.window(tag="startup_window"):

    #load text
    dpg.add_text("", tag="boot_text", wrap=600)

    #load image
    imagehelpers.load_pil_image("logo_texture", imagehelpers.retroify(locally("other/logo.png")).resize((50, 50)))
    dpg.add_image("logo_texture", pos=(270, 250), tag="logo_image")

def boot_sequence():
    def end_boot_sequence():
        dpg.hide_item("startup_window")
        dpg.show_item("main_window")
        dpg.set_primary_window("main_window", True)
        sound.play_sound(locally("sounds/beep1.wav"))

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
        
    sound.play_sound(locally("sounds/startup.wav"), 0.3)
    add_boot_text(METATEXT)
    add_boot_text(f"v{VERSION}")

    #LOAD SETTINGS
    add_boot_border("LOADING SETTINGS")
    try:
        with open(savepath('other/settings.json'), 'r', encoding='utf-8') as file:
            settings = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        try:
            with open(locally('other/settings.json'), 'r', encoding='utf-8') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            add_boot_text("loading with default settings...")
            settings = {
                "color1": [10, 10, 10],
                "color2": [40, 20, 5],
                "color3": [84, 41, 9],
                "color4": [250, 134, 55],
                "sfx_volume": 1,
                "noise": True
            }

    #sfx volume
    sound.sfx_volume = settings["sfx_volume"]; add_boot_text(f"sfx_volume: {sound.sfx_volume}")

    #theme colors
    state.color1 = tuple(settings["color1"])
    state.color2 = tuple(settings["color2"])
    state.color3 = tuple(settings["color3"])
    state.color4 = tuple(settings["color4"])
    state.noise = settings["noise"]
    set_theme(state.color1, state.color2, state.color3, state.color4)
    add_boot_text(f"color1: {state.color1}")
    add_boot_text(f"color2: {state.color2}")
    add_boot_text(f"color3: {state.color3}")
    add_boot_text(f"color4: {state.color4}")

    dpg.delete_item("logo_image")
    dpg.delete_item("logo_texture")
    
    imagehelpers.tint = state.color4
    imagehelpers.load_pil_image("logo_texture", imagehelpers.retroify(locally("other/logo.png")).resize((50, 50)))
    
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

#more noise shit
def animate_noise():
    while True:
        if state.noise:
            img = (imagehelpers.generate_noise(WIDTH, HEIGHT))
            data = [x/255.0 for x in img.convert("RGBA").tobytes()]
            dpg.set_value("noise_texture", data)
        else:
            dpg.set_value("noise_texture", [0.0] * (WIDTH * HEIGHT * 4))
        time.sleep(0.25)

with dpg.viewport_drawlist(front=True):
    dpg.draw_image("noise_texture", (0, 0), (WIDTH, HEIGHT))

#start noise
threading.Thread(target=animate_noise, daemon=True).start()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("startup_window", True)

dpg.hide_item("main_window")
threading.Thread(target=boot_sequence, daemon=True).start()

dpg.start_dearpygui()
dpg.destroy_context()