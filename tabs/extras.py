from dearpygui import dearpygui as dpg

from modules import audioshit as sound
from modules.state import *

def extras():

    def on_subtab_switch(_, app_data):
        sound.play_sound(locally("sounds/click.wav"))

    with dpg.tab_bar(tag="extras_bar", callback=on_subtab_switch):
        with dpg.tab(label="screenshots", tag="screenshots_tab"):
            pass
        with dpg.tab(label="radio", tag="radio_tab"):
            from tabs.extras_tab.radio import radio
            radio()
        with dpg.tab(label="minigame", tag="minigame_tab"):
            from tabs.extras_tab.minigame import minigame
            minigame()