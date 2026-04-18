from dearpygui import dearpygui as dpg
import time
import threading

from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules import state
from modules.state import *

def screenshots():
    def startup_viewer():
        done = False
        def waoiehfoipaugbp():
            while not done:
                dpg.set_value("viewer_loading_text", f"{t("POLLING...")} {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)

        loading_sound = sound.play_sound(locally("sounds/loading_.wav"))
        threading.Thread(target=waoiehfoipaugbp, daemon=True).start()
        state.screenie_ids = (match[0] for match in rq.search("(screenshots = True)")['matches'])
        done = True
        loading_sound.stop()
        
    dpg.add_button(label="startup screenshot viewer",
                   tag="viewer_button",
                   width=-1,
                   height=-1,
                   callback=startup_viewer)

    with dpg.child_window(tag="screenshot_window", width=-1, height=WIDTH-200):
        dpg.add_text(tag="viewer_loading_text")
        #TODO: make screenshot appear here
    dpg.hide_item("screenshot_window")

    
    #TODO: make search box for IDs with screenies
    dpg.hide_item(dpg.add_input_text(hint="search for index"))