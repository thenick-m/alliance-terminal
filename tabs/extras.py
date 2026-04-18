from dearpygui import dearpygui as dpg

from modules import audioshit as sound
from modules import state
from modules.state import *

def extras():

    def on_subtab_switch(_, app_data):
        sound.play_sound(locally("sounds/click.wav"))

    with dpg.tab_bar(tag="extras_bar", callback=on_subtab_switch):
        with dpg.tab(label="screenshots", tag="screenshots_tab"):
            from tabs.extras_tab.screenshots import screenshots
            screenshots()
        with dpg.tab(label="radio", tag="radio_tab"):
            from tabs.extras_tab.radio import radio
            radio()
        with dpg.tab(label="minigame", tag="minigame_tab"):
            from tabs.extras_tab.minigame import minigame
            minigame()
        with dpg.tab(label="credits"):
            def big_text(text):
                dpg.bind_item_font(dpg.add_text(text), state.big_font)

            def little_text(text):
                dpg.add_text(text)

            big_text("Programming")
            little_text("thenick_m - main programmer")
            little_text("willowself - original author & README.md")
            dpg.add_separator()
            big_text("Graphics")
            little_text("thenick_m - logo")
            little_text("cyfi205 - alli character")
            dpg.add_separator()
            big_text("Localization")
            little_text("lenkuti - es & fr")
            little_text("yuyuyut_p - pl")
            little_text("willowself - ru")

