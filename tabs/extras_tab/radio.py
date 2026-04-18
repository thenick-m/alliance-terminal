import threading
import time
import os

from dearpygui import dearpygui as dpg

from modules import audioshit as sound
from modules import requesthandler4000 as rq
from modules.state import *

import subprocess

def download_audio(url, filename):
    subprocess.run([
        savepath("other/yt-dlp.exe"),
        url,
        "--format", "worstaudio",
        "--output", savepath(f"other/radio/{filename}.mp3"),
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "48K",
        "--ffmpeg-location", locally("other"),
        "--quiet"
    ])

radio_thread = None
radio_active = False
radio_lock = threading.Lock()

radio_lines = []
def add_radio_line(text):
    def update_radio_line(text="", user="radio"):
        radio_lines.append(text)
        dpg.set_value("radio_line", "\n".join(f"{user}> {txt}" for txt in radio_lines))
        dpg.set_y_scroll("radio_line_window", -1.0)
        sound.play_sound(locally("sounds/blip2.wav"))
        time.sleep(0.03)

    #init
    if text == "/init":
        dpg.show_item("radio_line_window")
        dpg.show_item("radio_volume")


        for _ in range(15):
            update_radio_line()
        time.sleep(0.1)
        sound.play_sound(locally("sounds/click4.wav"))
        update_radio_line("radio started")
        update_radio_line("press 'connect radio' to connect")
    else:
        update_radio_line(text)

def play_radio_state(radio_state):
    filename = radio_state['url'].split("v=")[-1]
    path = os.path.normpath(savepath(f"other/radio/{filename}.mp3")) #normpath to fix shit

    if not os.path.exists(path):
        done = False
        def loading_sound():
            while not done:
                sound.play_sound(locally("sounds/blip2.wav"))
                time.sleep(0.5)
        add_radio_line("song not discovered in cache")
        add_radio_line("downloading...")
        threading.Thread(target=loading_sound, daemon=True).start()
        download_audio(radio_state['url'], filename)
        add_radio_line("download done")
        done = True
        sound.play_sound(locally("sounds/click4.wav"))
        time.sleep(0.2)

    sound.play_radio(path, radio_state['started_at'])
    print(path)

radio_generation = 0

def radio_loop(generation):
    current_url = None
    while radio_active and generation == radio_generation:
        radio_state = rq.get_radio_state()
        if radio_state['url'] != current_url:
            add_radio_line(f"got song: \n\n{radio_state['title']}\n...")
            current_url = radio_state['url']
            play_radio_state(radio_state)
            add_radio_line("now playing song")

        wake_at = radio_state['started_at'] + radio_state['duration']
        sleep_for = wake_at - time.time()
        if sleep_for > 0:
            time.sleep(sleep_for)
        else:
            time.sleep(2)

def radio():
    def larp_startup():
        sound.play_sound(locally("sounds/click2.wav"))

        dpg.disable_item("radio_button")
        add_radio_line("/init")
        dpg.configure_item("radio_button", label="connect radio", height=20, callback=activate_radio)
        dpg.enable_item("radio_button")

    def activate_radio():
        dpg.disable_item("radio_button")
        sound.play_sound(locally("sounds/click2.wav"))

        global radio_thread, radio_active, radio_generation

        if radio_active:
            return

        with radio_lock:
            if radio_active:
                return
            radio_active = True
            radio_generation += 1
            gen = radio_generation

        add_radio_line("starting radio...")
        radio_thread = threading.Thread(target=radio_loop, args=(gen,), daemon=True)
        radio_thread.start()

    def deactivate_radio():
        dpg.disable_item("radio_button")
        sound.play_sound(locally("sounds/click2.wav"))

        global radio_active
        radio_active = False
        sound.stop_radio()

        dpg.hide_item("radio_line_window")
        dpg.hide_item("radio_volume")

        dpg.configure_item("radio_button", label="connect radio", callback=activate_radio)
        sound.play_sound(locally("sounds/shutdown.wav"))
        dpg.enable_item("radio_button")

    def radio_volume_callback(_, app_data):

        sound.set_volume_radio(app_data/1.5)
        sound.radio_volume = app_data/1.5

    #UI
    with dpg.group(horizontal=True):
        dpg.hide_item(dpg.add_slider_float(
                    tag="radio_volume",
                    vertical=True,
                    default_value=sound.radio_volume,
                    format="%.1f",
                    height=235,
                    width=30,
                    min_value=0,
                    max_value=1,
                    callback=radio_volume_callback)
                    )
        with dpg.child_window(tag="radio_line_window", width=-1, height=235):
            dpg.add_text(tag="radio_line", wrap=280)
        dpg.hide_item("radio_line_window")

    dpg.add_button(label="startup radio", tag="radio_button", width=-1, height=-1, callback=larp_startup)
    dpg.hide_item(dpg.add_button(label="disconnect", tag="deactivate_radio", callback=deactivate_radio))