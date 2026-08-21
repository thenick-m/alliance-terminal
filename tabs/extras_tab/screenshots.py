from dearpygui import dearpygui as dpg
import time
import threading
import pyautogui
import base64
from PIL import Image
import io
import random

from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules import imagehelpers
from modules import state
from modules.state import *


def screenshots():
    current_pos = 0
    screenie_count = 1

    def startup_viewer():
        dpg.disable_item("viewer_button")
        sound.play_sound(locally("sounds/click4.wav"))
        try:
            done = False
            def waoiehfoipaugbp():
                nonlocal done
                while not done:
                    dpg.configure_item("viewer_button", label=f"{t("POLLING...")} {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                    time.sleep(0.1)

            loading_sound = sound.play_sound(locally("sounds/loading1.wav"))
            threading.Thread(target=waoiehfoipaugbp, daemon=True).start()

            result = rq.search("(screenshots = True)")

            loading_sound.stop()
            done = True
            if result == None:
                sound.play_sound(locally("sounds/error.wav"))
                sound.play_sound(locally("sounds/error2.wav"))

                dpg.configure_item("viewer_button", label=f"{t("ERROR")}: {t("couldn't contact server")}")
                time.sleep(1)
                return
            elif result.get("error", False):
                sound.play_sound(locally("sounds/error.wav"))
                sound.play_sound(locally("sounds/error2.wav"))

                dpg.configure_item("viewer_button", label=f"{t("ERROR")}: {t(result["error"])}")
                time.sleep(1)
                return
            else:
                result = result["matches"]

            done = True
            loading_sound.stop()

            if isinstance(result, dict):
                dpg.configure_item("viewer_button", label=t("ERROR"))
                sound.play_sound(locally("sounds/error2.wav"))
            else:
                sound.play_sound(locally("sounds/static.wav"))
                imagehelpers.channel_switch()

                state.screenie_ids = [entry[0] for entry in result]
                refresh_list("")

                dpg.hide_item("viewer_button")
                dpg.show_item("screenie_group")
        finally:
            dpg.enable_item("viewer_button")
            
    #autofill shit
    def filter_ids(text):
        text = text.lower()
        return [id for id in state.screenie_ids if text in id.lower()]
    
    def refresh_list(query=""):
        if not state.screenie_ids:
            return

        if query.strip():
            items = filter_ids(query)
        else:
            items = state.screenie_ids

        dpg.configure_item("screenie_list", items=items)

    def on_search_change(_, app_data):
        refresh_list(app_data)

    def on_list_click(_, app_data):
        sound.play_sound(locally("sounds/loading2.wav"), max_time=100)

        items = dpg.get_item_configuration("screenie_list")["items"]
        value = items[app_data] if isinstance(app_data, int) else app_data

        dpg.set_value("screenie_search", value)
        dpg.focus_item("screenie_search")

        threading.Timer(0.05, lambda: pyautogui.press("end")).start()

    def on_key_press(_, app_data):
        if app_data == dpg.mvKey_Return and (dpg.get_item_alias(dpg.get_value("extras_bar")) == "screenshots_tab"):

            text = dpg.get_value("screenie_search")
            results = filter_ids(text)

            if results:
                on_list_click(None, results[0])

    #screenie viewer
    def view_screenie(initial=True, increment=0):
        nonlocal current_pos
        nonlocal screenie_count
        if initial:
            current_pos = 0
            sound.play_sound(locally("sounds/submit5.wav"))

        split_shit = dpg.get_value("screenie_search").split()
        id = split_shit[0]
        
        if len(split_shit) == 2 and initial:
            current_pos = int(split_shit[1])        

        if not id:
            return
        
        dpg.disable_item("view_button")
        dpg.disable_item("s_bk")
        dpg.disable_item("s_fw")
        
        try:
            done = False
            def pawei0hrp9hwep():
                nonlocal done
                while not done:
                    dpg.set_value("viewer_loading_text", f"{t("POLLING...")} {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                    time.sleep(0.1)

            loading_sound = sound.play_sound(locally("sounds/loading1.wav")) if initial else sound.play_sound(locally("sounds/loading5.wav"), volume=sound.sfx_volume/2)
            threading.Thread(target=pawei0hrp9hwep, daemon=True).start()

            result = rq.get_screenie(id, current_pos)
            if result == None:
                sound.play_sound(locally("sounds/error.wav"))
                sound.play_sound(locally("sounds/error2.wav"))
                dpg.set_value("viewer_loading_text", f"{t("ERROR")}: {t("couldn't contact server")}")
                done = True
                loading_sound.stop()
                current_pos -= increment
                return

            done = True
            loading_sound.stop()

            if "error" in result.keys():
                sound.play_sound(locally("sounds/error.wav"))
                sound.play_sound(locally("sounds/error2.wav"))
                dpg.set_value("viewer_loading_text", f"{t("ERROR")}: {result["error"]}")
                done = True
                loading_sound.stop()
                current_pos -= increment
                return
            else:
                screenie_count = result["count"]
                update_buttons()

                def q329rhpq4tbp():
                    time.sleep(0.5)
                    state.shake_viewport(intensity=1.5, duration=2, falloff=False)
                    for _ in range(19):
                        dpg.set_value("viewer_loading_text", " ".join(f"{random.randint(0, 255):02X}" for _ in range(36)))
                        time.sleep(0.05); dpg.set_value("viewer_loading_text", ""); time.sleep(0.05)
                        dpg.set_value("viewer_loading_text", f"{current_pos}/{result["count"]-1}\n{t("Note")}: {result["note"]}")
                
                if initial:
                    sound.play_sound(locally("sounds/loading3.wav"))
                    threading.Thread(target=q329rhpq4tbp, daemon=True).start()
                    time.sleep(1)

            #decode the thing
            image_bytes = base64.b64decode(result["image"])

            img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

            data = img.getdata()

            texture_data = []
            for pixel in data:
                texture_data.extend([channel / 255 for channel in pixel])

            #show image
            if len(texture_data) != 300 * 300 * 4:
                sound.play_sound(locally("sounds/error.wav"))
                sound.play_sound(locally("sounds/error2.wav"))
                dpg.set_value("viewer_loading_text", f"{t("ERROR")}: bad texture size")
                done = True
                loading_sound.stop()
                current_pos -= increment
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
                dpg.set_value("screenshot_texture", tex)
                time.sleep(0.2)
            dpg.set_value("screenshot_texture", texture_data)
            screen_sound.stop()

            if not initial:
                dpg.set_value("viewer_loading_text", f"{current_pos}/{result["count"]-1}\n{t("Note")}: {result["note"]}")
        finally:
            dpg.enable_item("view_button")
            update_buttons()
            done = True

    def update_buttons():
        if current_pos <= 0:
            dpg.disable_item("s_bk")
        else:
            dpg.enable_item("s_bk")

        if current_pos >= screenie_count - 1:
            dpg.disable_item("s_fw")
        else:
            dpg.enable_item("s_fw")

    def next_screenie():
        nonlocal current_pos
        sound.play_sound(locally("sounds/submit4.wav"))

        if current_pos < screenie_count - 1:
            current_pos += 1

        update_buttons()
        view_screenie(initial=False, increment=1)

    def prev_screenie():
        nonlocal current_pos
        sound.play_sound(locally("sounds/submit4.wav"))

        if current_pos > 0:
            current_pos -= 1

        update_buttons()
        view_screenie(initial=False)

    #UI
    dpg.add_button(label=t("startup screenshot viewer"),
                tag="viewer_button",
                width=-1,
                height=-1,
                callback=startup_viewer)
    with dpg.group(tag="screenie_group"):
        
        with dpg.group(horizontal=True):
            with dpg.child_window(width=WIDTH//2, height=WIDTH-200):
                dpg.add_image("screenshot_texture", tag="screenie_image", width=165, height=145)
            with dpg.group():
                with dpg.child_window(width=-1, height=WIDTH-250):
                    dpg.add_text(tag="viewer_loading_text", wrap=WIDTH//2-60) #text
                with dpg.group(horizontal=True):
                    dpg.disable_item(dpg.add_button(tag="s_bk", label="<", width=WIDTH//2//2-22, height=40, callback=prev_screenie))
                    dpg.add_button(tag="s_fw", label=">", width=-1, height=40, callback=next_screenie)
        
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_input_text(tag="screenie_search", hint=f"<{t("index")}> <{t("screenshot")}>", callback=on_search_change, width=200)
                dpg.add_listbox([], tag="screenie_list", callback=on_list_click, width=200)
            dpg.add_button(tag="view_button", label=t("view"), width=-1, height=-1, callback=view_screenie)

        with dpg.handler_registry():
            dpg.add_key_press_handler(callback=on_key_press)
    dpg.hide_item("screenie_group")