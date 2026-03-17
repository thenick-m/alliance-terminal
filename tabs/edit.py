from dearpygui import dearpygui as dpg
import time
import threading


from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules import state
from modules.state import *

def edit():    
    def login():
        sound.play_sound(locally("sounds/click2.wav"))
        loading_sound = sound.play_sound(locally("sounds/startup3.wav"))

        with dpg.window(label="log in", modal=True, no_close=True,
                        no_resize=True, no_move=True,
                        tag="discord_thinking_window",
                        pos=(WIDTH//2 - 90, WIDTH//2 - 30),
                        min_size=(150, 150),
                        max_size=(150, 150)):
            dpg.add_text("Verify through discord on your web browser to confirm your enrollment.",
                            tag="login_loading_text",
                            wrap=150)

        def do_login():
            counter = 0
            while not done[0] and counter < 30:
                time.sleep(0.1)
                counter += 0.1
            loading_sound.stop()
            

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("login_loading_text", text)

            if result == None:
                set_text("ERROR: couldn't contact server")
            elif result == False:
                set_text("ERROR: login failed")
            elif 'error' in result.keys():
                set_text(f"ERROR: {result['error']}")
            elif not result['is_editor']:
                set_text("ERROR: you are not enrolled")
            else:
                print(result)
                set_text(f"Welcome, {result["username"]}")
                sound.play_sound(locally("sounds/shutdown.wav"))
                sound.play_sound(locally("sounds/welcome.wav"))

                time.sleep(1.2)
                sound.play_sound(locally("sounds/fractal_block_world_welcome.wav"))

                time.sleep(3)

                dpg.delete_item("discord_thinking_window")
                dpg.hide_item("login_button")

                dpg.show_item("numpad_edit")

                dpg.add_text(tag="editor_flash", label="EDITOR MODE", pos=(WIDTH//2-50, WIDTH//2-37), parent="main_window")
                for _ in range(3):
                    dpg.set_value("editor_flash", "EDITOR MODE")
                    time.sleep(1)
                    dpg.set_value("editor_flash", "")
                    time.sleep(1)


                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))
            sound.play_sound(locally("sounds/shutdown.wav"))

            time.sleep(3)

            dpg.hide_item("discord_thinking_window")                       

        threading.Thread(target=do_login, daemon=True).start()
        run_async(lambda: rq.editor_login(), on_complete)

    def update_leaderboard(sender, app_data):
        sound.play_sound(locally("sounds/click2.wav"))

        dpg.hide_item("update_leaderboard_button")

        def do_update():
            loading_sound = sound.play_sound(locally("sounds/loading1.wav"))
            while not done[0]:
                dpg.set_value("leaderboard_loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)
            loading_sound.stop()
            sound.play_sound(locally("sounds/receipt.wav"))

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("leaderboard_loading_text", text)

            if result == None:
                set_text("ERROR: couldn't contact server")
            elif 'error' in result.keys():
                set_text(f"ERROR: {result['error']}")
            else:
                for i, user in enumerate(result["leaderboard"]):
                    dpg.add_separator(parent="leaderboard_window")

                    place = dpg.add_text(f"{i+1}: {user["username"]}", parent="leaderboard_window")
                    dpg.add_text(f"Contributions: {user["contributions"]}", parent="leaderboard_window")

                    dpg.add_separator(parent="leaderboard_window")
                    if i < 3:
                        dpg.bind_item_font(place, state.big_font)
                dpg.hide_item("leaderboard_loading_text")
                dpg.show_item("update_leaderboard_button")
                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))
            dpg.show_item("update_leaderboard_button")
                

        threading.Thread(target=do_update, daemon=True).start()
        run_async(lambda: rq.leaderboard(), on_complete)

    current = ""
    def numpad_press(sender, app_data):
        sound.play_sound(locally("sounds/click3.wav"))
        nonlocal current

        key = sender[:-5] #chop off the end
        if key == "AC":
            sound.play_sound(locally("sounds/clear.wav"))
            dpg.set_value("index_input", "")
            current = ""
        else:
            dpg.set_value("index_input", current + key)
            current = current + key

    #UI

    dpg.add_button(label="log in through discord", tag="login_button", width=-1, height=100, callback=login)

    #only show after login
    with dpg.child_window(tag="numpad_edit", width=-1, height=230):
        dpg.add_input_text(tag="index_input", hint="index", width=-1)

        with dpg.group(horizontal=True):

            with dpg.group():
                with dpg.group(horizontal=True):
                    for num in ["7","8","9"]:
                        dpg.add_button(tag=f"{num}_edit", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["4","5","6"]:
                        dpg.add_button(tag=f"{num}_edit", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["1","2","3"]:
                        dpg.add_button(tag=f"{num}_edit", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["-","0","AC"]:
                        dpg.add_button(tag=f"{num}_edit", label=num, width=55, height=44,
                                    callback=numpad_press)
            
            dpg.add_button(label="edit", width=-1, height=-1, callback=lambda: print("hi"))
    dpg.hide_item("numpad_edit")

    with dpg.child_window(width=-1, height=-1, tag="leaderboard_window"):
        dpg.add_text("[ LEADERBOARD ]")
        dpg.add_separator()
        dpg.add_button(label="update", tag="update_leaderboard_button", width=-1, height=20, callback=update_leaderboard)
        dpg.add_text(tag="leaderboard_loading_text")