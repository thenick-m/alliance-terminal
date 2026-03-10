from dearpygui import dearpygui as dpg
import threading
import pyautogui
import time

from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules.state import *
from modules import state

from tabs.get import populate_get_tab

def search():
    operators = field_data["operators"]
    field_values = {k.lower(): v for k, v in field_data["fields"].items()}
    fields = list(field_values.keys())
    resource_fields = field_data["resource_fields"]

    #add present to non-boolean fields
    for field, values in field_values.items():
        if values != ["true", "false"] and values != [] and "present" not in values:
            values.append("present")

    for field in fields: #add the rest of the fields
        if field in field_values.keys():
            continue
        else:
            field_values[field] = []


    for field, value in field_values.items(): #add present to everything
        if value == ["true", "false"]:
            continue
        else:
            value.append("present")
            field_values[field] = value

    complete_conditions = []

    def switch_search_view(sender, app_data):

        if state.search_results_view:
            sound.play_sound(locally("sounds/submit4.wav"))

            dpg.configure_viewport(0, width=WIDTH, height=WIDTH)

            state.search_results_view = False
            dpg.hide_item("loading_text")
            dpg.hide_item("results_panel")
            dpg.hide_item("back_button")
            dpg.show_item("condition_and_button")
            dpg.show_item("submit_button")
            dpg.show_item("query_input")
            dpg.show_item("suggestion_list")
        else:
            
            state.search_results_view = True
            dpg.hide_item("condition_and_button")
            dpg.hide_item("query_input")
            dpg.hide_item("suggestion_list")
            dpg.show_item("loading_text")
    
    #get text suggestions for command line
    def get_suggestions(text):
        if text.endswith(" "): #stuff for making sure the autofill updates after enter is pressed
            parts = text.strip().split(" ")
            parts.append("")
        else:
            parts = text.strip().split(" ")
        
        if len(parts) == 1:
            return [f for f in fields if f.startswith(parts[0])]
        elif len(parts) == 2:
            return [op for op in operators if op.startswith(parts[1])]
        elif len(parts) == 3:
            field = parts[0]
            return [v for v in field_values.get(field, []) if v.startswith(parts[2])]
        
        return []
    
    def on_input_change(sender, app_data):
        suggestions = get_suggestions(app_data)
        
        dpg.configure_item("suggestion_list", items=suggestions)

    def on_suggestion_click(sender, app_data):
        sound.play_sound(locally("sounds/loading2.wav"), max_time=100)

        #parse the query input
        current = dpg.get_value("query_input")
        if current.endswith(" "):
            parts = current.strip().split(" ")
            parts.append(app_data)
        else:
            parts = current.strip().split(" ")
            parts[-1] = app_data

        new_value = " ".join(parts)

        if len(parts) >= 3:
            sound.play_sound(locally("sounds/submit3.wav"))
            #submit and clear
            complete_conditions.append(new_value)
            dpg.configure_item("condition_list", items=complete_conditions)
            dpg.set_value("query_input", "")
            dpg.configure_item("suggestion_list", items=[])
            dpg.focus_item("query_input")
        else:
            dpg.set_value("query_input", new_value + " ")
            dpg.focus_item("query_input")

            #this is a hack to get around highlighting
            threading.Timer(0.05, lambda: pyautogui.press("end")).start()

    def on_key_press(sender, app_data):
        #only activate if its supposed to
        if not state.search_results_view and (dpg.get_item_alias(dpg.get_value("tab_bar")) == "search_tab") and (app_data == dpg.mvKey_Return): 
            text = dpg.get_value("query_input")
            suggestions = get_suggestions(text)

            if suggestions:
                on_suggestion_click(None, suggestions[0])

            #check if the condition is valid ok
            query_input:str = dpg.get_value("query_input").strip()
            if len(query_input.split(" ")) >= 3:
                sound.play_sound(locally("sounds/submit3.wav"))

                #submit and clear
                complete_conditions.append(query_input)
                dpg.configure_item("condition_list", items=complete_conditions)
                dpg.set_value("query_input", "")
                dpg.configure_item("suggestion_list", items=[])
                dpg.focus_item("query_input")

    def on_key_release(sender, app_data):
        if dpg.is_item_focused("query_input"):
            on_input_change(None, dpg.get_value("query_input"))

    def on_condition_click(sender, app_data):
        sound.play_sound(locally("sounds/submit4.wav"))

        #delete tjhat shit yk what im sayn 😂
        complete_conditions.pop(complete_conditions.index(app_data))
        dpg.configure_item("condition_list", items=complete_conditions)

    def submit_search(sender, app_data): #TODO: move this shit into another module

        sound.play_sound(locally("sounds/submit5.wav"))

        if not complete_conditions:
            return
        
        searchStringArg = " ".join([f"({condition})" for condition in complete_conditions])
        print(complete_conditions)

        switch_search_view(0, 0)

        def populate_results(results):

            def pretty_results_from_dict(results_dict):
                return "\n".join([f"{key}: {value}" for key, value in results_dict.items()])

            sound.play_sound(locally("sounds/reciept1.wav"))
            sound.play_sound(locally("sounds/success.wav"))

            dpg.set_value("loading_text", f"{len(results)} results {'(MAX)' if len(results) == 100 else ''}")
            dpg.show_item("results_panel")
            dpg.show_item("back_button")
            dpg.delete_item("results_panel", children_only=True)

            #dict of matches
            results_dict = {result[0]: result[1] for result in results}

            #copied sorting code from x4a
            results = [(tuple([int(id_num) for id_num in result[0].split("-")]), result[1]) for result in results] #turn StarID into int tuple
            results = sorted(results) #sort matches
            results = [("-".join([str(id_num) for id_num in result[0]]), result[1]) for result in results] #turn int tuple into StarID

            for i, result in enumerate(results):
                
                #cleanse results for display
                result_to_display = result[1].copy()
                if "Name" in result_to_display:
                    del result_to_display["Name"]
                for key in list(result_to_display.keys()):
                    if key in resource_fields:
                        del result_to_display[key]

                resource_dict = {key: result[1][key] for key in result[1] if key in resource_fields}

                child = dpg.add_child_window(parent="results_panel", width=300, height=400, border=True, tag=f"result_{i}")

                dpg.add_text(
                    f"{result[0]} {result[1].get('Name', 'No Name')}",
                    parent=child,
                    wrap=180,
                    tag=f"{result[0]}_result_title"
                )
                dpg.bind_item_font(f"{result[0]}_result_title", big_font)

                dpg.add_text(
                    f"\n{pretty_results_from_dict(result_to_display)}",
                    parent=child,
                    wrap=180
                )

                def change_get_planet(sender, app_data):
                    sound.play_sound(locally("sounds/click2.wav"))
                    populate_get_tab(results_dict[sender])  #sets state.current_get_planet internally
                    dpg.set_value("tab_bar", "get_tab")

                dpg.add_button(label="get", width=80, height=300, tag=f"{result[0]}", parent=child, pos=(210, 10),
                            callback=change_get_planet)
                
            dpg.configure_viewport(0, width=WIDTH, height=HEIGHT)

        def do_search():
            loading_sound = sound.play_sound(locally("sounds/loading2.wav"))
            while not done[0]:
                dpg.set_value("loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)
            loading_sound.stop()

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("loading_text", text)

            if result == None:
                set_text("ERROR: couldn't contact server")
            elif 'error' in result.keys():
                set_text(f"ERROR: {result['error']}")
            else:
                populate_results(result['matches'])
                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))
            dpg.show_item("back_button")
                

        threading.Thread(target=do_search, daemon=True).start()
        run_async(lambda: rq.search(searchStringArg), on_complete)

    with dpg.handler_registry():
        dpg.add_key_release_handler(callback=on_key_release)
        dpg.add_key_press_handler(callback=on_key_press)
        dpg.add_mouse_wheel_handler(callback=lambda sender, app_data: sound.play_sound(locally("sounds/scroll.wav"), max_time=50))

    #UI
    with dpg.group(parent="search_tab"):
                                
        dpg.add_text(tag="loading_text")
        dpg.hide_item("loading_text")

        with dpg.child_window(tag="results_panel", width=-1, height=570, border=True):
            dpg.hide_item("results_panel")

        dpg.add_button(label="back", tag="back_button",
                    callback=switch_search_view,
                    width=-1,
                    height=20)
        dpg.hide_item("back_button")

        with dpg.group(horizontal=True, tag="condition_and_button"):
            dpg.add_listbox([], tag="condition_list",
                            callback=on_condition_click,
                            width=200, num_items=9)
            
            dpg.add_button(label="submit", tag="submit_button",
                        callback=submit_search,
                        width=100,
                        height=170)

        dpg.add_input_text(tag="query_input", #query
                        hint="<field> <operator> <value>",
                        callback=on_input_change,
                        on_enter=True,
                        width=200)
        
        dpg.add_listbox([], tag="suggestion_list", #autofill
                        callback=on_suggestion_click,
                        width=150)