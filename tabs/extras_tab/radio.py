import threading
import time
import os

from dearpygui import dearpygui as dpg
from PIL import Image

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
        "--write-thumbnail",
        "--convert-thumbnails", "jpg",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "48K",
        "--ffmpeg-location", locally("other"),
        "--quiet"
    ], creationflags=subprocess.CREATE_NO_WINDOW)

radio_thread = None
radio_active = False
radio_lock = threading.Lock()

radio_lines = []
def add_radio_line(text):
    def update_radio_line(text=""):
        radio_lines.append(text)
        dpg.set_value("radio_line", "\n".join(txt for txt in radio_lines))
        sound.play_sound(locally("sounds/blip2.wav"))

    #init
    if text == "/init":
        dpg.show_item("radio_group")
        dpg.show_item("radio_volume")

        time.sleep(0.1)
        sound.play_sound(locally("sounds/click4.wav"))
        update_radio_line(t("radio started"))
        update_radio_line(t("press 'connect radio' to connect"))
    else:
        update_radio_line(text)
        time.sleep(0.03)

def clear_lines():
    global radio_lines; radio_lines = []
    dpg.set_value("radio_line", radio_lines)

def set_radio_image(path):

    img = Image.open(path).convert("RGBA")
    img = img.resize((300, 300), Image.Resampling.LANCZOS)

    data = img.getdata()

    texture_data = []
    for pixel in data:
        texture_data.extend([channel / 255 for channel in pixel])

    #show image
    if len(texture_data) != 300 * 300 * 4:
        return
    
    def make_texture(img, size):
        small = img.resize((size, size), Image.Resampling.NEAREST)
        upscaled = small.resize((300, 300), Image.Resampling.NEAREST)

        arr = np.array(upscaled, dtype=np.float32) / 255.0
        return arr.flatten()

    screen_sound = sound.play_sound(locally("sounds/loading4.wav"))
    levels = [8, 15, 30, 60, 120, 300]
    for size in levels:
        tex = make_texture(img, size)
        dpg.set_value("radio_texture", tex)
        time.sleep(0.2)
    dpg.set_value("radio_texture", texture_data)
    screen_sound.stop()

def play_radio_state(radio_state):
    filename = radio_state['url'].split("v=")[-1]
    path = os.path.normpath(savepath(f"other/radio/{filename}.mp3")) #normpath to fix shit

    if not os.path.exists(path):
        done = False
        def loading_sound():
            while not done:
                sound.play_sound(locally("sounds/blip2.wav"))
                time.sleep(0.5)
        add_radio_line(f"{t("downloading")}...")
        threading.Thread(target=loading_sound, daemon=True).start()
        download_audio(radio_state['url'], filename)
        done = True
        sound.play_sound(locally("sounds/click4.wav"))
        time.sleep(0.2)

    sound.play_radio(path, radio_state['started_at'])
    print(path)
    threading.Thread(target=set_radio_image, args=(f"{path}.jpg",)).start()

def progress_bar_update_loop(started_at, duration, sleep_for):
    global radio_active

    updates = 60
    for _ in range(updates):
        if not radio_active:
            return

        progress = (time.time()-started_at)/duration

        progress = max(0.0, min(1.0, progress))

        dpg.set_value("radio_progress", progress)

        time.sleep(sleep_for / updates)


radio_generation = 0

def radio_loop(generation):
    current_url = None
    while radio_active and generation == radio_generation:
        radio_state = rq.get_radio_state()
        if radio_state['url'] != current_url:
            clear_lines()
            add_radio_line(f"{radio_state['title']}\n{t("duration")}: {'{:d}:{:02d}'.format(*divmod(radio_state['duration'], 60))}\n{t("contributor")}: {radio_state['contributor']}\n")
            current_url = radio_state['url']
            play_radio_state(radio_state)
            add_radio_line(t("now playing song"))

        wake_at = radio_state['started_at'] + radio_state['duration']
        sleep_for = wake_at - time.time()
        if sleep_for > 0:
            threading.Thread(target=progress_bar_update_loop, args=(radio_state["started_at"], radio_state["duration"], sleep_for)).start()
            time.sleep(sleep_for)
        else:
            time.sleep(2)

def radio():
    def larp_startup():
        sound.play_sound(locally("sounds/click2.wav"))

        dpg.hide_item("radio_button")
        dpg.configure_item("radio_button_2", label=t("connect radio"), callback=activate_radio)
        add_radio_line("/init")

    def activate_radio():
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

        add_radio_line(f"{t("starting radio")}...")
        radio_thread = threading.Thread(target=radio_loop, args=(gen,), daemon=True)
        radio_thread.start()
        dpg.configure_item("radio_button_2", label=t("disconnect"), callback=deactivate_radio)
        dpg.show_item("radio_group")
        dpg.show_item("radio_volume")
        dpg.hide_item("radio_button")

    def deactivate_radio():
        clear_lines()
        dpg.disable_item("radio_button")
        sound.play_sound(locally("sounds/click2.wav"))

        global radio_active
        radio_active = False
        sound.stop_radio()

        dpg.hide_item("radio_group")
        dpg.hide_item("radio_volume")

        dpg.configure_item("radio_button", label=t("connect radio"), callback=activate_radio)
        dpg.show_item("radio_button")
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
                    height=260,
                    width=30,
                    min_value=0,
                    max_value=1,
                    callback=radio_volume_callback)
                    )
        with dpg.group(tag="radio_group"): #TODO: rebuild this piece of shit
            with dpg.child_window(tag="radio_line_window", width=-1, height=125):
                dpg.add_text(tag="radio_line")

            dpg.add_progress_bar(tag="radio_progress", width=-1, height=10)
            
            with dpg.group(horizontal=True):
                with dpg.child_window(height=-1, width=115, no_scrollbar=True, no_scroll_with_mouse=True):
                    dpg.add_image("radio_texture", width=100, height=100)

                dpg.add_button(tag="radio_button_2", label=t("disconnect"), width=-1, height=-1, callback=deactivate_radio)

        dpg.hide_item("radio_group")

    dpg.add_button(label=t("startup radio"), tag="radio_button", width=-1, height=-1, callback=larp_startup)