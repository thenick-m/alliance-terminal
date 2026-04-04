from dearpygui import dearpygui as dpg
import time
import threading

from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules import state
from modules.state import *

from tabs.extras_tab import minigame as mg_module

def extras():

    def on_subtab_switch(_, app_data):
        sound.play_sound(locally("sounds/click.wav"))
        tab = dpg.get_item_alias(app_data)
        if tab == "minigame_tab":
            if mg_module.tab_enter: mg_module.tab_enter()
        else:
            if mg_module.tab_exit: mg_module.tab_exit()

    with dpg.tab_bar(tag="extras_bar", callback=on_subtab_switch):
        with dpg.tab(label="screenshots", tag="screenshots_tab"):
            pass
        with dpg.tab(label="minigame", tag="minigame_tab"):
            from tabs.extras_tab.minigame import minigame
            minigame()