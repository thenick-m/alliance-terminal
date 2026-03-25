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

                time.sleep(0 if state.debug else 1.2)
                sound.play_sound(locally("sounds/fractal_block_world_welcome.wav"))

                time.sleep(0 if state.debug else 3)

                dpg.delete_item("discord_thinking_window")
                dpg.hide_item("login_button")

                dpg.show_item("numpad_edit")

                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))
            sound.play_sound(locally("sounds/shutdown.wav"))

            time.sleep(3)

            dpg.hide_item("discord_thinking_window") 

        threading.Thread(target=do_login, daemon=True).start()

        if state.debug:
            on_complete({
                "is_editor": True,
                "username": "debug_mode"
                })
        else:
            run_async(lambda: rq.editor_login(), on_complete)

    def update_leaderboard():
        sound.play_sound(locally("sounds/click2.wav"))

        dpg.hide_item("update_leaderboard_button")

        def do_update():

            #show the shit
            dpg.show_item("leaderboard_loading_text")

            #clear the stuff
            dpg.delete_item("leaderboard_entries", children_only=True)

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
                    dpg.add_separator(parent="leaderboard_entries")

                    place = dpg.add_text(f"{i+1}: {user["username"]}", parent="leaderboard_entries")
                    dpg.add_text(f"Contributions: {user["contributions"]}", parent="leaderboard_entries")

                    dpg.add_separator(parent="leaderboard_entries")
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

    #EDIT SHIT

    edit_args = {}
    original_fields = set()

    def switch_edit_view():
        if state.current_edit_planet: 
            dpg.hide_item("leaderboard_window")
            dpg.hide_item("numpad_edit")

            dpg.show_item("edit_window")
            dpg.show_item("back_edit")
            dpg.show_item("submit_edit")
            dpg.show_item("edit_fields")
            dpg.show_item("field_value_edits")
            dpg.show_item("back_submit")
        else: #numpad & leaderboard
            dpg.hide_item("edit_window")
            dpg.hide_item("back_edit")
            dpg.hide_item("edit_loading_text")
            dpg.hide_item("submit_edit")

            dpg.show_item("leaderboard_window")
            dpg.show_item("numpad_edit")

    def back_to_numpad():
        sound.play_sound(locally("sounds/submit4.wav"))
        state.current_edit_planet = None
        state.current_edit_index = None
        switch_edit_view()

        dpg.hide_item("edit_loading_text_error")
        dpg.set_value("edit_loading_text_error", "ERROR")

        dpg.hide_item("edit_back_button_error")
        dpg.hide_item("edit_back_button")

    def back_to_edit():
        sound.play_sound(locally("sounds/submit4.wav"))

        dpg.hide_item("edit_loading_text")
        dpg.hide_item("edit_back_button_error")
        dpg.hide_item("edit_back_button")
        
        dpg.hide_item("edit_loading_text_error")
        dpg.set_value("edit_loading_text_error", "ERROR")

        dpg.show_item("edit_window")
        dpg.show_item("back_edit")
        dpg.show_item("submit_edit")
        dpg.show_item("edit_fields")
        dpg.show_item("field_value_edits")
        dpg.show_item("back_submit")

    def delete_field(field, tag):
        sound.play_sound(locally("sounds/submit4.wav"))
        dpg.delete_item(tag)
        print(f"deleting item {tag}")
        edit_args.pop(field, None)
        new_field_args.pop(field, None)
        

    def populate_edit_tab(planet):
        state.current_edit_planet = planet

        edit_args.clear()
        original_fields.clear()
        new_field_args.clear()

        if planet == 1:
            planet = {}

            def woatfhalb():
                dpg.show_item("edit_loading_text")
                dpg.set_value("edit_loading_text", "Index doesn't exist, client-side template:")
                time.sleep(3)
                dpg.hide_item("edit_loading_text")


            threading.Thread(target=woatfhalb, daemon=True).start()

        #clear edit_fields
        dpg.delete_item("edit_fields", children_only=True)

        #fill edit_fields
        dpg.add_text("[ NEW FIELDS ]", parent="edit_fields")

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_group(tag="new_edit_fields", parent="edit_fields")

        #separate data

        physical = {
            "Gravity": planet.get("Gravity"),
            "Radius": planet.get("Radius"),
            "Moons": planet.get("Moons"),
        }

        environment = {
            "Atmosphere": planet.get("Atmosphere"),
            "Oceans": planet.get("Oceans"),
            "Tectonics": planet.get("Tectonics"),
            "Life": planet.get("Life"),
        }

        resource_fields = state.field_data["resource_fields"]
        resource_fields_normalized = [f.lower() for f in resource_fields]

        deposit_fields = ["Lime", "Quartz", "Saltpeter", "Limestone", "Saltground", "Trees", "Quartz"]

        deposit_resources = {k: v for k, v in planet.items() if k in deposit_fields}

        numeric_resources = {k: v for k, v in planet.items() if k.lower() in resource_fields_normalized and not isinstance(v, bool)}
        
        known_fields = set(physical.keys()) | set(environment.keys()) | set(resource_fields) | set(deposit_fields) | {"Name", "StarID", "Index", "PlanetID", "PlanetCount"}
        other = {k: v for k, v in planet.items() if k not in known_fields}

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_text("[ PHYSICAL ]", parent="edit_fields")
        if physical:
            for field, result in physical.items():
                if result is not None:
                    tag = f"field_row_{field}"
                    with dpg.child_window(parent="edit_fields", width=-1, height=30, no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="X", width=20, height=20,
                                        user_data=(field, tag),
                                        callback=lambda s, a, u: delete_field(u[0], u[1]))
                            dpg.add_text(field)
                        edit_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(120, 5))
                        original_fields.add(field)
                        dpg.set_value(edit_args[field], result)

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_text("[ ENVIRONMENT ]", parent="edit_fields")
        if environment:
            for field, result in environment.items():
                if result is not None:
                    tag = f"field_row_{field}"
                    with dpg.child_window(parent="edit_fields", width=-1, height=30, no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="X", width=20, height=20,
                                        user_data=(field, tag),
                                        callback=lambda s, a, u: delete_field(u[0], u[1]))
                            dpg.add_text(field)
                        edit_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(120, 5))
                        original_fields.add(field)
                        dpg.set_value(edit_args[field], result)

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_text("[ OTHER ]", parent="edit_fields")
        if other:
            for field, result in other.items():
                if result is not None:
                    tag = f"field_row_{field}"
                    with dpg.child_window(parent="edit_fields", width=-1, height=30, no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="X", width=20, height=20,
                                        user_data=(field, tag),
                                        callback=lambda s, a, u: delete_field(u[0], u[1]))
                            dpg.add_text(field)
                        edit_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(120, 5))
                        original_fields.add(field)
                        dpg.set_value(edit_args[field], result)

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_text("[ RESOURCES ]", parent="edit_fields")
        if numeric_resources:
            for field, result in numeric_resources.items():
                if result is not None:
                    tag = f"field_row_{field}"
                    with dpg.child_window(parent="edit_fields", width=-1, height=30, no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="X", width=20, height=20,
                                        user_data=(field, tag),
                                        callback=lambda s, a, u: delete_field(u[0], u[1]))
                            dpg.add_text(field)
                        edit_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(120, 5))
                        original_fields.add(field)
                        dpg.set_value(edit_args[field], result)

        dpg.add_separator(parent="edit_fields")
        dpg.add_separator(parent="edit_fields")

        dpg.add_text("[ DEPOSITS ]", parent="edit_fields")
        if deposit_resources:
            for field, result in deposit_resources.items():
                if result is not None:
                    tag = f"field_row_{field}"
                    with dpg.child_window(parent="edit_fields", width=-1, height=30, no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="X", width=20, height=20,
                                        user_data=(field, tag),
                                        callback=lambda s, a, u: delete_field(u[0], u[1]))
                            dpg.add_text(field)
                        edit_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(120, 5))
                        original_fields.add(field)
                        dpg.set_value(edit_args[field], result)


    current = ""
    def numpad_press(sender):
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

    def submit_edit_get():
        sound.play_sound(locally("sounds/submit5.wav"))

        index = dpg.get_value("index_input")

        if index:
            index = index.strip()
        else:
            return

        def do_edit():
            dpg.hide_item("numpad_edit")
            dpg.hide_item("leaderboard_window")
            dpg.show_item("edit_loading_text")
            loading_sound = sound.play_sound(locally("sounds/loading2.wav"))
            while not done[0]:
                dpg.set_value("edit_loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)
            loading_sound.stop()
            sound.play_sound(locally("sounds/receipt.wav"))
            sound.play_sound(locally("sounds/success.wav"))

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("edit_loading_text", text)

            print(result)
            if result == None:
                set_text("couldn't contact server")
            elif 'error' in result.keys():
                if result['error'] == 'no matches found': #no planet found
                    populate_edit_tab(1)
                    switch_edit_view()
                    state.current_edit_index = index
                    return
                else:
                    set_text(f"{result['error']}")
            else:
                populate_edit_tab(result['planet'])
                switch_edit_view()
                dpg.hide_item("edit_loading_text")
                state.current_edit_index = index
                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))

            dpg.show_item("edit_loading_text_error")
            dpg.show_item("edit_back_button_error")                      

                

        threading.Thread(target=do_edit, daemon=True).start()
        run_async(lambda: rq.get(index), on_complete)

    def submit_edit():
        sound.play_sound(locally("sounds/submit5.wav"))

        dpg.hide_item("edit_fields")
        dpg.hide_item("back_submit")
        dpg.hide_item("field_value_edits")
        
        dpg.hide_item("edit_back_button")
        dpg.hide_item("edit_back_button_error")
        dpg.hide_item("edit_loading_text_error")
        dpg.hide_item("edit_loading_text")

        if state.current_edit_planet == 1:
            state.current_edit_planet = {}

        args = {field.capitalize(): str(value)
                for field, value in state.current_edit_planet.items()
                if field.lower() in original_fields or field in original_fields}

        new_args = {field.capitalize(): str(dpg.get_value(field_input))
                    for field, field_input in edit_args.items()}

        
        def dict_diff(dict_a, dict_b): #gets the difference between two dicts
            result = {
                'added': {k: dict_b[k] for k in dict_b.keys() - dict_a.keys()},
                'removed': {k: dict_a[k] for k in dict_a.keys() - dict_b.keys()},
                'value_diffs': {k: dict_b[k] for k in dict_a.keys() & dict_b.keys() if dict_a[k] != dict_b[k]}
            }
            return result
        
        edits = dict_diff(args, new_args)

        #format edit args (putting it directly into the old discord bot formatter bc lazy)

        send_out = []
        send_out += [f"({k} = {v})" for k, v in edits['added'].items()]
        send_out += [f"({k} = {v})" for k, v in edits['value_diffs'].items()]
        send_out += [f"({k} = /DEL)" for k in edits['removed'].keys()]

        edit_string = f"{state.current_edit_index} {" ".join(send_out)}"
        print(edit_string)

        def do_edit():
            loading_sound = sound.play_sound(locally("sounds/loading2.wav"))
            dpg.show_item("edit_loading_text")
            while not done[0]:
                dpg.set_value("edit_loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)
            loading_sound.stop()

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("edit_loading_text", text)

            if result == None:
                set_text("couldn't contact server")
            elif 'error' in result.keys():
                set_text(f"{result['error']}")
            else:
                set_text(result['summary'])

                sound.play_sound(locally("sounds/reciept1.wav"))
                sound.play_sound(locally("sounds/success.wav"))

                dpg.show_item("edit_back_button_error")
                dpg.show_item("edit_back_button")

                dpg.set_value("edit_loading_text_error", "SUCCESS")
                dpg.show_item("edit_loading_text_error")

                def waluifhruifb():
                    for _ in range(10):
                        dpg.set_value("edit_loading_text_error", "SUCCESS !!!")
                        time.sleep(0.5)
                        dpg.set_value("edit_loading_text_error", "SUCCESS")
                        time.sleep(0.5)

                threading.Thread(target=waluifhruifb, daemon=True).start()

                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))

            dpg.show_item("edit_back_button_error")
            dpg.show_item("edit_back_button")
            dpg.show_item("edit_loading_text_error")


        threading.Thread(target=do_edit, daemon=True).start()
        run_async(lambda: rq.edit(edit_string), on_complete)
        
        

    #AUTOFILL SHIT
    field_values = {k.lower(): v for k, v in field_data["fields"].items()}
    all_fields = list(field_values.keys())
    new_field_args = {}  #separate dict for new fields added via the inputs for convenicen

    def add_field_input_changed(_, app_data):
        suggestions = [f for f in all_fields if f.startswith(app_data.lower())]
        dpg.configure_item("suggestion_list_edit", items=suggestions)

    def add_value_input_changed(_, app_data):
        field = dpg.get_value("add_field_edit").lower()
        values = field_values.get(field, [])
        suggestions = [v for v in values if str(v).startswith(app_data.lower())]
        dpg.configure_item("suggestion_list_edit", items=suggestions)

    def on_add_suggestion_click(_, app_data):
        sound.play_sound(locally("sounds/loading2.wav"), max_time=100)

        #TODO: fix whatever is making this not fucking work
        if dpg.is_item_focused("add_field_edit") or not dpg.get_value("add_field_edit"):
            dpg.set_value("add_field_edit", app_data)
            field = app_data.lower()
            values = field_values.get(field, [])
            dpg.configure_item("suggestion_list_edit", items=values)
            dpg.focus_item("add_value_edit")
        else:
            #fill value and commit
            dpg.set_value("add_value_edit", app_data)
            commit_new_field()

    def commit_new_field():
        field = dpg.get_value("add_field_edit").strip()
        value = dpg.get_value("add_value_edit").strip()

        if not field:
            return
        
        if field in edit_args:
            def awiguairhg():
                sound.play_sound(locally("sounds/error2.wav"))
                dpg.set_value("add_field_edit", "")
                dpg.set_value("add_value_edit", "")
                dpg.configure_item("suggestion_list_edit", items=[])
                dpg.focus_item("add_field_edit")

                dpg.show_item("edit_loading_text")
                dpg.set_value("edit_loading_text", "ERROR: field already present")
                time.sleep(3)
                dpg.hide_item("edit_loading_text") 
            threading.Thread(target=awiguairhg, daemon=True).start()
            return

        sound.play_sound(locally("sounds/submit3.wav"))


        #add row to the new_edit_fields group
        tag = f"field_row_{field}"
        with dpg.child_window(parent="new_edit_fields", width=-1, height=30,
                              no_scrollbar=True, no_scroll_with_mouse=True, tag=tag):
            with dpg.group(horizontal=True):
                dpg.add_button(label="X", width=20, height=20,
                            user_data=(field, tag),
                            callback=lambda _, __, u: delete_field(u[0], u[1]))
                dpg.add_text(field.capitalize())
            new_field_args[field] = dpg.add_input_text(hint="any", width=-1, pos=(100, 5))
            dpg.set_value(new_field_args[field], value)

        #also register in main edit_args so submit picks it up
        edit_args[field] = new_field_args[field]
        original_fields.add(field)

        #clear inputs
        dpg.set_value("add_field_edit", "")
        dpg.set_value("add_value_edit", "")
        dpg.configure_item("suggestion_list_edit", items=[])
        dpg.focus_item("add_field_edit")

    def on_add_field_key(_, app_data):
        if app_data == dpg.mvKey_Return:
            suggestions = dpg.get_item_configuration("suggestion_list_edit")["items"]

            if suggestions:
                on_add_suggestion_click(None, suggestions[0])
                return

            #commit directly
            field = dpg.get_value("add_field_edit").strip()
            value = dpg.get_value("add_value_edit").strip()
            if field and value:
                commit_new_field()
            elif field and not value:
                dpg.focus_item("add_value_edit")




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
            
            dpg.add_button(label="edit", width=-1, height=-1, callback=submit_edit_get)
    dpg.hide_item("numpad_edit")

    #actual edit child window
    dpg.bind_item_font(dpg.add_text("ERROR", tag="edit_loading_text_error"), state.big_font)
    dpg.hide_item("edit_loading_text_error")

    dpg.hide_item(dpg.add_text(tag="edit_loading_text")) #loading text
    dpg.hide_item(dpg.add_button(tag="edit_back_button_error", label="back to numpad", height=20, width=-1, callback=back_to_numpad))
    dpg.hide_item(dpg.add_button(tag="edit_back_button", label="back to edit", height=20, width=-1, callback=back_to_edit))

    with dpg.child_window(width=-1, height=-1, tag="edit_window", border=False):

        #input text
        with dpg.group(tag="field_value_edits", horizontal=True):
            with dpg.group():
                dpg.bind_item_font(dpg.add_input_text(tag="add_field_edit", hint="<field>", width=200, height=30, callback=add_field_input_changed), state.big_font)
                dpg.bind_item_font(dpg.add_input_text(tag="add_value_edit", hint="<value>", width=200, height=30, callback=add_value_input_changed), state.big_font)

            #autofill item
            dpg.add_listbox(items=[], tag="suggestion_list_edit", width=-1, callback=on_add_suggestion_click)
    
        with dpg.child_window(width=-1, height=500, tag="edit_fields"):
            pass #populate_edit_tab fills the other fields later

        #bottom
        with dpg.child_window(tag="back_submit"):
            with dpg.group(horizontal=True):
                dpg.add_button(label="back to numpad", width=WIDTH//2-10, height=-1, tag="back_edit", callback=back_to_numpad)
                dpg.add_button(label="submit edit", width=-1, height=-1, tag="submit_edit", callback=submit_edit)



    dpg.hide_item("edit_window")

    with dpg.child_window(width=-1, height=-1, tag="leaderboard_window"):
        dpg.add_text("[ LEADERBOARD ]")
        dpg.add_separator()
        dpg.add_button(label="update", tag="update_leaderboard_button", width=-1, height=20, callback=update_leaderboard)
        dpg.add_text(tag="leaderboard_loading_text")

        #leaderboard entries
        dpg.add_group(tag="leaderboard_entries")

    with dpg.handler_registry():
        dpg.add_key_press_handler(callback=on_add_field_key)