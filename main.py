from dearpygui import dearpygui as dpg
import time
import threading
import random
import json

from modules import requesthandler4000 as rq
from modules.state import *
from modules import state #reimport cached state module into namespace for redundancy
from modules import audioshit as sound
from modules import imagehelpers

METATEXT = "x4AllianceTerminal by thenick_m & willow"
VERSION = "0.2.0"

settings = {}

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
    color1_set=(20, 13, 8),
    color2_set=(40, 20, 5),
    color3_set=(84, 41, 9),
    color4_set=(250, 134, 55)
    ):

    state.color1 = color1_set
    state.color2 = color2_set
    state.color3 = color3_set
    state.color4 = color4_set

    crt_theme = make_theme(color1_set, color2_set, color3_set, color4_set)

    dpg.bind_theme(crt_theme)

# --- MAIN ---

#start gui
dpg.create_context()

#set theme
set_theme()

#font config
with dpg.font_registry():
    with dpg.font(locally("other/fixedsys.ttf"), 14) as default_font:
        pass
    with dpg.font(locally("other/fixedsys.ttf"), 25) as big_font:
        state.big_font = big_font

dpg.bind_font(default_font)

#texture config mainly for noise shit
with dpg.texture_registry():
    initial = imagehelpers.generate_retro_boi(WIDTH, HEIGHT).convert("RGBA")
    data = [x/255.0 for x in initial.tobytes()]
    dpg.add_dynamic_texture(WIDTH, HEIGHT, data, tag="noise_texture")


# --- MAIN WINDOW ---
with dpg.window(label="x4at", tag="main_window"):

    def go_through_quit():
        dpg.configure_viewport(0, width=WIDTH, height=WIDTH)
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
            global settings
            settings["color1"] = state.color1
            settings["color2"] = state.color2
            settings["color3"] = state.color3
            settings["color4"] = state.color4
            settings["sfx_volume"] = sound.sfx_volume
            settings["noise"] = state.noise
            settings["colorbars"] = state.colorbars
            settings["token"] = rq.discord_token if rq.discord_token else 0

            json.dump(settings, file, indent=4) #saveshit

        add_boot_text("shutting down program...")
        time.sleep(0.5)
        dpg.stop_dearpygui()

    dpg.add_button(tag="quit_button", label="quit", pos=(305, 5), callback=go_through_quit)

    def on_tab_switch(_, app_data):
        sound.play_sound(locally("sounds/click.wav"))
        sound.play_sound(locally("sounds/switch.wav"))
        imagehelpers.channel_switch()

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

        elif tab == "edit_tab":
            dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)

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
            
            with dpg.child_window(horizontal_scrollbar=True, width=-1, height=165, tag="themes"):
                dpg.add_text("[ THEMES ]")
                with dpg.group(horizontal=True, tag="weoihauipuiwfgbouirg"):
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
                            sound.play_sound(locally("sounds/beep2.wav"))
                            set_theme(self.color1, self.color2, self.color3, self.color4)
                            imagehelpers.channel_switch()

                        def add(self):
                            button = dpg.add_button(label=self.name, width=100, height=-1, callback=lambda: self.change_theme())
                            dpg.bind_item_theme(button, self.theme)

                        def remove_custom(self):
                            global settings

                            dpg.delete_item(self.window)
                            del settings["themes"][self.name]

                            sound.play_sound(locally("sounds/submit4.wav"))

                        def add_custom(self):
                            with dpg.child_window(parent="custom_themes", width=150) as window:

                                with dpg.group(horizontal=True):

                                    dpg.add_button(label="X", width=20, height=-1, callback=self.remove_custom)
                                    button = dpg.add_button(label=self.name, width=100, height=-1, callback=lambda: self.change_theme())
                                    self.window = window
                                    dpg.bind_item_theme(button, self.theme)


                    Theme("phosphor", (20, 13, 8), (40, 20, 5), (84, 41, 9), (250, 134, 55)).add()
                    Theme("byte", (20, 35, 29), (85, 101, 81), (150, 167, 134), (215, 233, 186)).add()
                    Theme("gold", (50, 25, 0), (100, 50, 25), (200, 100, 50), (255, 200, 100)).add()
                    Theme("girly girl", (54, 42, 53), (112, 89, 110), (161, 127, 158), (255, 183, 197)).add()
                    Theme("manly man", (10, 10, 13), (75, 75, 94), (139, 139, 174), (204, 204, 255)).add()
                    Theme("emo bart", (22, 22, 22), (129, 129, 129), (27, 20, 35), (237, 237, 237)).add()

                    #custom theme entry box
                    def submit_custom_theme():
                        global settings

                        color1 = dpg.get_value("color1")
                        color2 = dpg.get_value("color2")
                        color3 = dpg.get_value("color3")
                        color4 = dpg.get_value("color4")

                        color1 = tuple([int(''.join(filter(str.isdigit, string))) for string in color1.split()])
                        color2 = tuple([int(''.join(filter(str.isdigit, string))) for string in color2.split()])
                        color3 = tuple([int(''.join(filter(str.isdigit, string))) for string in color3.split()])
                        color4 = tuple([int(''.join(filter(str.isdigit, string))) for string in color4.split()])

                        name = dpg.get_value("custom_theme_name_input")

                        theme = Theme(name, color1, color2, color3, color4)

                        theme.change_theme()
                        theme.add_custom()

                        settings["themes"][name] = [list(color1), list(color2), list(color3), list(color4)]


                    with dpg.child_window(height=-1, width=200, parent="weoihauipuiwfgbouirg"):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_input_text(tag="color1", hint="r g b (bg)", width=100)
                                dpg.add_input_text(tag="color2", hint="r g b (mid 1)", width=100)
                                dpg.add_input_text(tag="color3", hint="r g b (mid 2)", width=100)
                                dpg.add_input_text(tag="color4", hint="r g b (main)", width=100)

                            with dpg.group():
                                dpg.add_input_text(hint="name", width=-1, tag="custom_theme_name_input")
                                dpg.add_button(label="custom", width=-1, height=-1, callback=submit_custom_theme)

                    with dpg.child_window(horizontal_scrollbar=True, width=400, height=-1):
                        dpg.add_text("[ CUSTOM THEMES ]")
                        dpg.add_group(horizontal=True, tag="custom_themes")

            dpg.add_separator()

            def change_volume(_, app_data):

                sound.play_sound(locally("sounds/scroll.wav"), max_time=50)

                sound.sfx_volume = app_data

            dpg.add_slider_float(
                tag="sfx_volume_slider",
                label="sfx volume",
                default_value=1,
                min_value=0,
                max_value=1,
                callback=change_volume
                )
            
            def toggle_noise():
                sound.play_sound(locally("sounds/switch2.wav"))
                state.noise = not state.noise

            dpg.add_separator()

            dpg.add_checkbox(tag="retro_effects_toggle", label="retro effects", callback=toggle_noise, default_value=state.noise)

            def toggle_color_bars():
                sound.play_sound(locally("sounds/switch2.wav"))
                state.colorbars = not state.colorbars

            dpg.add_separator()

            dpg.add_checkbox(tag="colorbars_toggle", label="colored resource bars", callback=toggle_color_bars, default_value=state.colorbars)

            def log_out():
                global settings

                settings["token"] = 0
                rq.discord_token = None

                with open(savepath('other/settings.json'), 'w', encoding='utf-8') as file:

                    json.dump(settings, file, indent=4)

                dpg.hide_item("numpad_edit")
                dpg.show_item("login_button")
                dpg.hide_item("log_out")

                sound.play_sound(locally("sounds/shutdown.wav"))
                

            dpg.add_separator()

            dpg.hide_item(dpg.add_button(label="log out", tag="log_out", callback=log_out))
            
            def sales_demolition():
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
    global settings

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
                "color1": [20, 13, 8],
                "color2": [40, 20, 5],
                "color3": [84, 41, 9],
                "color4": [250, 134, 55],
                "themes": {},
                "sfx_volume": 1,
                "noise": True,
                "colorbars": False,
                "token": 0
            }

    #load custom themes
    for name, theme in settings["themes"].items():
        Theme(name, tuple(theme[0]), tuple(theme[1]), tuple(theme[2]), tuple(theme[3])).add_custom()

    #sfx volume
    sound.sfx_volume = settings["sfx_volume"]; add_boot_text(f"sfx_volume: {sound.sfx_volume}")
    dpg.set_value("sfx_volume_slider", sound.sfx_volume)

    #editor
    rq.discord_token = settings["token"] if settings["token"] else None

    #editor gui
    if rq.discord_token:
        dpg.show_item("numpad_edit")
        dpg.hide_item("login_button")

    #theme colors
    state.color1 = tuple(settings["color1"])
    state.color2 = tuple(settings["color2"])
    state.color3 = tuple(settings["color3"])
    state.color4 = tuple(settings["color4"])
    add_boot_text(f"color1: {state.color1}")
    add_boot_text(f"color2: {state.color2}")
    add_boot_text(f"color3: {state.color3}")
    add_boot_text(f"color4: {state.color4}")

    #noise
    state.noise = settings["noise"]
    dpg.set_value("retro_effects_toggle", state.noise)

    #colorbars
    state.colorbars = settings["colorbars"]
    dpg.set_value("colorbars_toggle", state.colorbars)

    imagehelpers.channel_switch()
    sound.play_sound(locally("sounds/static.wav"))
    set_theme(state.color1, state.color2, state.color3, state.color4)

    dpg.delete_item("logo_image")
    dpg.delete_item("logo_texture")
    
    imagehelpers.load_pil_image("logo_texture", imagehelpers.retroify(locally("other/logo.png")).resize((50, 50)))
    
    dpg.add_image("logo_texture", pos=(270, 250), tag="logo_image", parent="startup_window")


    add_boot_text("starting main window...")
    time.sleep(0.1)
    
    time.sleep(0.5)
    end_boot_sequence()
    

dpg.create_viewport(title="x4AllianceTerminal", 
                    small_icon=locally("other/logo.ico"), 
                    large_icon=locally("other/logo.ico"), 
                    width=WIDTH, height=WIDTH,
                    x_pos=1500, 
                    always_on_top=True,
                    min_width=WIDTH,
                    max_width=WIDTH,
                    min_height=WIDTH,
                    max_height=HEIGHT) #no fullscreen no fullscreen NO FULLSCREEN NO FUCKING FULLSCREEN

#more noise shit
def animate_noise():
    while True:
        if state.noise:
            dpg.show_item("noise_draw")
            img = imagehelpers.generate_retro_boi(WIDTH, HEIGHT)
            data = [x/255.0 for x in img.convert("RGBA").tobytes()]
            dpg.set_value("noise_texture", data)

        else:
            dpg.hide_item("noise_draw")
        time.sleep(0.25)

with dpg.viewport_drawlist(front=True):
    dpg.draw_image("noise_texture", (0, 0), (WIDTH, HEIGHT), tag="noise_draw")

#start noise
threading.Thread(target=animate_noise, daemon=True).start()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("startup_window", True)

dpg.hide_item("main_window")
threading.Thread(target=boot_sequence, daemon=True).start()

#framerate shit

target_fps = 45
frame_time = 1.0 / target_fps

while dpg.is_dearpygui_running():
    frame_start = time.perf_counter()
    dpg.render_dearpygui_frame()
    elapsed = time.perf_counter() - frame_start
    sleep_time = frame_time - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

dpg.destroy_context()