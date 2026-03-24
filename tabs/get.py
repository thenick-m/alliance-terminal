from dearpygui import dearpygui as dpg
import time
import threading


from modules import requesthandler4000 as rq
from modules import audioshit as sound
from modules import state
from modules.state import *

resource_fields = state.field_data["resource_fields"]

def switch_get_view():
    if state.current_get_planet: 
        dpg.show_item("get_tab_content")
        dpg.show_item("back_get")

        dpg.hide_item("numpad")
        dpg.hide_item("get_loading_text")

        dpg.configure_viewport(0, width=state.WIDTH, height=state.HEIGHT)
    else: #numpad
        dpg.hide_item("get_tab_content")
        dpg.hide_item("back_get")
        dpg.show_item("numpad")
        dpg.hide_item("get_loading_text")
        dpg.configure_viewport(0, width=state.WIDTH, height=state.WIDTH)
        
def populate_get_tab(planet):

    dpg.delete_item("get_tab_content", children_only=True) #clear

    if not planet:
        dpg.add_text("No planet selected", parent="get_tab_content")
        return

    #separate data
    name = planet.get("Name", "No Name")
    star_id = planet.get("StarID", "N/A")
    index = planet.get("Index", "N/A")
    planet_id = planet.get("PlanetID", "N/A")
    planet_count = planet.get("PlanetCount", "N/A")

    physical = {
        "Gravity": planet.get("Gravity", "N/A"),
        "Radius": planet.get("Radius", "N/A"),
        "Moons": planet.get("Moons", "N/A"),
    }

    environment = {
        "Atmosphere": planet.get("Atmosphere", "N/A"),
        "Oceans": planet.get("Oceans", "N/A"),
        "Tectonics": planet.get("Tectonics", "N/A"),
        "Life": planet.get("Life", "N/A"),
    }

    resource_fields_normalized = [f.lower() for f in resource_fields]

    deposit_fields = ["Lime", "Quartz", "Saltpeter", "Limestone", "Saltground", "Trees", "Quartz"]

    deposit_resources = {k: v for k, v in planet.items() if k in deposit_fields}

    numeric_resources = {k: v for k, v in planet.items() if k.lower() in resource_fields_normalized and not isinstance(v, bool)}
    
    known_fields = set(physical.keys()) | set(environment.keys()) | set(resource_fields) | set(deposit_fields) | {"Name", "StarID", "Index", "PlanetID", "PlanetCount"}
    other = {k: v for k, v in planet.items() if k not in known_fields}
    

    # --- HEADER ---
    dpg.add_text(f"{name}", tag="planet_name_header", parent="get_tab_content")
    dpg.bind_item_font("planet_name_header", big_font)
    dpg.add_text(f"Star {star_id}  |  Planet {planet_id}/{planet_count}  |  Index {index}", 
                parent="get_tab_content")
    dpg.add_separator(parent="get_tab_content")

    #physical stats list
    stats_graph = dpg.add_child_window(parent="get_tab_content", width=-1, height=200, border=True)
    dpg.add_text("[ PHYSICAL ]", parent=stats_graph)
    dpg.add_separator(parent=stats_graph)
    for key, val in physical.items():
        if val is not None:
            dpg.add_text(f"{key:<10} {val}", parent=stats_graph)

    dpg.add_text("", parent=stats_graph)
    dpg.add_text("[ ENVIRONMENT ]", parent=stats_graph)
    dpg.add_separator(parent=stats_graph)
    for key, val in environment.items():
        if val is not None:
            display = str(val).lower() if isinstance(val, bool) else val
            dpg.add_text(f"{key:<10} {display}", parent=stats_graph)

    dpg.add_text("", parent=stats_graph)
    dpg.add_text("[ OTHER ]", parent=stats_graph)
    dpg.add_separator(parent=stats_graph)
    for key, val in other.items():
        if val is not None:
            display = str(val).lower() if isinstance(val, bool) else val
            dpg.add_text(f"{key:<10} {display}", parent=stats_graph, wrap=300)

    dpg.add_separator(parent="get_tab_content")

    #numeric resources bar chart
    
    resource_graph = dpg.add_child_window(parent="get_tab_content", width=-1, height=230, border=True)

    #header with toggle button
    header_group = dpg.add_group(horizontal=True, parent=resource_graph)
    dpg.add_text("[ RESOURCES ]", parent=header_group)
    dpg.add_button(label="text", tag="resource_toggle", parent=header_group, width=-1,
                callback=lambda: toggle_resource_view(numeric_resources))
    
    dpg.add_separator(parent=resource_graph)

    resource_view = ["graph"]  #list so it's mutable from nested function

    def toggle_resource_view(numeric_resources):
        sound.play_sound(locally("sounds/click2.wav"))
        if resource_view[0] == "graph":
            resource_view[0] = "text"
            dpg.set_item_label("resource_toggle", "graph")
            dpg.hide_item("resource_plot_container")
            dpg.show_item("resource_text_container")
            dpg.hide_item("get_legend")
        else:
            resource_view[0] = "graph"
            dpg.set_item_label("resource_toggle", "text")
            dpg.show_item("resource_plot_container")
            dpg.hide_item("resource_text_container")
            dpg.show_item("get_legend")

    resource_plot_container = dpg.add_group(parent=resource_graph, tag="resource_plot_container")
    if numeric_resources:
        plot = dpg.add_plot(height=150, width=-1, parent=resource_plot_container,
                        no_menus=True, no_box_select=True, no_mouse_pos=True, no_inputs=True)
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, parent=plot, tag="get_x_axis", no_gridlines=True)
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, parent=plot, tag="get_y_axis", no_gridlines=True)

        present_fields = []
        known_fields = []
        present_x = []
        known_x = []
        present_y = []
        known_y = []

        all_fields = list(numeric_resources.keys())
        for j, (key, val) in enumerate(numeric_resources.items()):
            if val == "Present" or val == "present":
                present_fields.append(key)
                present_x.append(float(j))
                present_y.append(1.0)
            else:
                known_fields.append(key)
                known_x.append(float(j))
                known_y.append(float(val))

        if known_x:
            dpg.add_bar_series(x=known_x, y=known_y, weight=0.7,
                            label="Known", parent=y_axis)

        if present_x:
            series = dpg.add_bar_series(x=present_x, y=present_y, weight=0.7,
                                    label="Present", parent=y_axis)
            with dpg.theme() as present_theme:
                with dpg.theme_component(dpg.mvBarSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Fill,
                                    state.color4+(100,),
                                    category=dpg.mvThemeCat_Plots)
            dpg.bind_item_theme(series, present_theme)

        #shorten fields
        for i in range(len(all_fields)):
            all_fields[i] = f"{all_fields[i][:4]}."

        dpg.set_axis_ticks("get_x_axis", 
                        tuple(zip(all_fields, [float(j) for j in range(len(all_fields))])))
        dpg.set_axis_limits("get_x_axis", -0.5, len(all_fields) - 0.5)
        dpg.fit_axis_data("get_y_axis")
        legend_group = dpg.add_group(horizontal=True, parent=resource_graph)
        dpg.add_text("[half-shaded] = Unknown\n[fully-shaded] = Known", parent=legend_group, tag="get_legend")
    else:
            dpg.add_text(f"No resources logged", parent=resource_plot_container)


    #text container
    resource_text_container = dpg.add_group(parent=resource_graph, tag="resource_text_container", show=False)
    if numeric_resources:
        for key, val in numeric_resources.items():
            display = "present" if val in ["Present", "present"] else str(val)
            dpg.add_text(f"{key:<12} {display}", parent=resource_text_container)
    else:
            dpg.add_text(f"No resources logged", parent=resource_text_container)

    #deposits
    dpg.add_separator(parent="get_tab_content")
    deposit_container = dpg.add_child_window(parent="get_tab_content", height=60)
    dpg.add_text("[ DEPOSITS ]", parent=deposit_container)
    bool_group = dpg.add_group(parent=deposit_container)
    if deposit_resources:
        dpg.add_text("".join([f"{key}, " for key in deposit_resources.keys()]), parent=bool_group)
    else:
        dpg.add_text(f"None", parent=bool_group)

    state.current_get_planet = planet
    switch_get_view()

def get():
    #UI
    dpg.hide_item(dpg.add_child_window(tag="get_tab_content", width=-1, height=590, border=False))

    current = ""
    def numpad_press(sender):
        sound.play_sound(locally("sounds/click3.wav"))
        nonlocal current

        key = sender
        if key == "AC":
            sound.play_sound(locally("sounds/clear.wav"))
            dpg.set_value("planet_id_input", "")
            current = ""
        else:
            dpg.set_value("planet_id_input", current + key)
            current = current + key

    def submit_get():
        sound.play_sound(locally("sounds/submit5.wav"))

        index = dpg.get_value("planet_id_input")

        if index:
            index = index.strip()
        else:
            return

        def do_get():
            dpg.hide_item("numpad")
            dpg.show_item("get_loading_text")
            loading_sound = sound.play_sound(locally("sounds/loading2.wav"))
            while not done[0]:
                dpg.set_value("get_loading_text", f"POLLING... {['/', '-', '\\', '|'][int((time.perf_counter()*4)%4)]}")
                time.sleep(0.1)
            loading_sound.stop()
            sound.play_sound(locally("sounds/receipt.wav"))
            sound.play_sound(locally("sounds/success.wav"))

        done = [False]

        def on_complete(result):
            done[0] = True

            def set_text(text):
                dpg.set_value("get_loading_text", text)

            if result == None:
                set_text("couldn't contact server")
            elif 'error' in result.keys():
                set_text(f"{result['error']}")
            else:
                populate_get_tab(result['planet'])
                switch_get_view()
                dpg.hide_item("get_loading_text")
                return
            
            sound.play_sound(locally("sounds/error.wav"))
            sound.play_sound(locally("sounds/error2.wav"))

            dpg.show_item("get_loading_text_error")
            dpg.show_item("back_get")
                

        threading.Thread(target=do_get, daemon=True).start()
        run_async(lambda: rq.get(index), on_complete)

    dpg.bind_item_font(dpg.add_text("ERROR", tag="get_loading_text_error"), state.big_font)
    dpg.hide_item("get_loading_text_error")
        
    dpg.hide_item(dpg.add_text(tag="get_loading_text", parent="get_tab"))

    with dpg.child_window(tag="numpad", width=-1, height=230):
        dpg.add_input_text(tag="planet_id_input", hint="index", width=-1)

        with dpg.group(horizontal=True):

            with dpg.group():
                with dpg.group(horizontal=True):
                    for num in ["7","8","9"]:
                        dpg.add_button(tag=f"{num}", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["4","5","6"]:
                        dpg.add_button(tag=f"{num}", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["1","2","3"]:
                        dpg.add_button(tag=f"{num}", label=num, width=55, height=44,
                                    callback=numpad_press)
                with dpg.group(horizontal=True):
                    for num in ["-","0","AC"]:
                        dpg.add_button(tag=f"{num}", label=num, width=55, height=44,
                                    callback=numpad_press)
            
            dpg.add_button(label="submit", width=-1, height=-1, callback=submit_get)

    
    #make button for returning to numpad
    def back_to_numpad():
        sound.play_sound(locally("sounds/submit4.wav"))

        dpg.hide_item("get_loading_text_error")
        
        state.current_get_planet = None
        switch_get_view()

    dpg.hide_item(dpg.add_button(tag="back_get", label="back to numpad", width=-1, height=20, callback=back_to_numpad))