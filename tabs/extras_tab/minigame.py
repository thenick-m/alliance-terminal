from dearpygui import dearpygui as dpg
import random
import threading
import time

from modules import audioshit as sound
from modules import state
from modules import imagehelpers
from modules.state import *

COLS     = 10
ROWS     = 10
CELL     = 18
PAD      = 8
CANVAS_W = COLS * CELL + PAD * 2
CANVAS_H = ROWS * CELL + PAD * 2

tab_enter = None
tab_exit  = None

def minigame():
    global tab_enter, tab_exit

    # --- state ---
    maze          = {}
    player        = [0, 0]
    end_pos       = [ROWS-1, COLS-1]
    game_active   = [False]
    trail = []

    # --- maze generation ---
    def is_solvable():
        from collections import deque

        def slide_destinations(r, c):
            destinations = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                cr, cc = r, c
                while True:
                    if not can_move(cr, cc, dr, dc):
                        break
                    cr, cc = cr+dr, cc+dc
                if (cr, cc) != (r, c):
                    destinations.append((cr, cc))
            return destinations

        visited = set()
        queue   = deque([(0, 0)])
        visited.add((0, 0))

        while queue:
            r, c = queue.popleft()
            if r == end_pos[0] and c == end_pos[1]:
                return True
            for nr, nc in slide_destinations(r, c):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False

    def generate_maze():
        while True:
            maze.clear()
            for r in range(ROWS):
                for c in range(COLS):
                    maze[(r,c)] = {'walls': [True, True, True, True]}

            visited = set()
            def carve(r, c):
                visited.add((r, c))
                dirs = [(0,1,1,3),(1,0,2,0),(0,-1,3,1),(-1,0,0,2)]
                random.shuffle(dirs)
                for dr, dc, ws, wn in dirs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and (nr,nc) not in visited:
                        maze[(r,c)]['walls'][ws]   = False
                        maze[(nr,nc)]['walls'][wn] = False
                        carve(nr, nc)
            carve(0, 0)

            if is_solvable():
                break

    def new_maze():
        generate_maze()
        trail.clear()
        player[0], player[1] = 0, 0
        draw_maze()
        sound.play_sound(locally("sounds/beep1.wav"))

    # --- drawing ---
    def cell_px(r, c):
        return PAD + c * CELL, PAD + r * CELL

    def draw_maze():
        if not dpg.does_item_exist("maze_drawlist"):
            return
        dpg.delete_item("maze_drawlist", children_only=True)

        bg  = (*state.color1, 255)
        col = (*state.color4, 255)

        #background
        dpg.draw_rectangle((0,0), (CANVAS_W, CANVAS_H),
                           fill=bg, color=bg, parent="maze_drawlist")

        #start tint
        sx, sy = cell_px(0, 0)
        dpg.draw_rectangle((sx,sy), (sx+CELL,sy+CELL),
                           fill=(*state.color2, 200), color=(*state.color2, 200),
                           parent="maze_drawlist")

        #end tint
        ex, ey = cell_px(*end_pos)
        dpg.draw_rectangle((ex,ey), (ex+CELL,ey+CELL),
                           fill=(*state.color3, 255), color=(*state.color3, 255),
                           parent="maze_drawlist")

        #walls
        for r in range(ROWS):
            for c in range(COLS):
                x, y  = cell_px(r, c)
                walls = maze[(r,c)]['walls']  #T R B L
                t     = 1.5
                if walls[0]: dpg.draw_line((x,y),      (x+CELL,y),      color=col, thickness=t, parent="maze_drawlist")
                if walls[1]: dpg.draw_line((x+CELL,y), (x+CELL,y+CELL), color=col, thickness=t, parent="maze_drawlist")
                if walls[2]: dpg.draw_line((x,y+CELL), (x+CELL,y+CELL), color=col, thickness=t, parent="maze_drawlist")
                if walls[3]: dpg.draw_line((x,y),      (x,y+CELL),      color=col, thickness=t, parent="maze_drawlist")

        draw_player()

    def draw_player():
        if not dpg.does_item_exist("maze_drawlist"):
            return
        if dpg.does_item_exist("player_dot"):
            dpg.delete_item("player_dot")
        r, c   = player
        x, y   = cell_px(r, c)
        cx, cy = x + CELL//2, y + CELL//2
        dpg.draw_circle((cx,cy), CELL//2 - 3,
                        fill=(*state.color4, 255),
                        color=(*state.color4, 255),
                        parent="maze_drawlist",
                        tag="player_dot")
        
    def draw_trail_cell(r, c):
        if not dpg.does_item_exist("maze_drawlist"):
            return
        x, y   = cell_px(r, c)
        cx, cy = x + CELL//2, y + CELL//2
        dpg.draw_circle((cx, cy), CELL//2 - 3,
                        fill=(*state.color3, 80),
                        color=(*state.color3, 80),
                        parent="maze_drawlist")

    # --- movement ---
    def can_move(r, c, dr, dc):
        wall_idx = {(-1,0): 0, (0,1): 1, (1,0): 2, (0,-1): 3}
        return not maze[(r,c)]['walls'][wall_idx[(dr,dc)]]

    def move(dr, dc):
        if not game_active[0]:
            return

        moved = False
        while True:
            r, c = player
            if not can_move(r, c, dr, dc):
                break
            nr, nc = r+dr, c+dc
            pos = (r, c)
            if pos not in trail:
                trail.append(pos)
                draw_trail_cell(r, c)
            player[0], player[1] = nr, nc
            moved = True

        if moved:
            sound.play_sound(locally("sounds/blip.wav"))
            draw_player()

            if check_end():
                return

    def check_end():
        if player[0] == end_pos[0] and player[1] == end_pos[1]:
            sound.play_sound(locally("sounds/success.wav"))
            imagehelpers.channel_switch(0.25)
            threading.Timer(0.4, new_maze).start()
            return True
        return False

    # --- keyboard ---
    def on_key_press(_, app_data):
        if not game_active[0]:
            return
        k = app_data
        if   k == dpg.mvKey_Up    or k == dpg.mvKey_W: move(-1,  0)
        elif k == dpg.mvKey_Down  or k == dpg.mvKey_S: move( 1,  0)
        elif k == dpg.mvKey_Left  or k == dpg.mvKey_A: move( 0, -1)
        elif k == dpg.mvKey_Right or k == dpg.mvKey_D: move( 0,  1)

    # --- tab lifecycle ---
    def start_game():
        game_active[0] = True
        if not maze:
            new_maze()

    def stop_game():
        game_active[0] = False

    tab_enter = start_game
    tab_exit  = stop_game

    # --- UI ---
    dpg.add_separator(parent="minigame_tab")
    
    with dpg.group(parent="minigame_tab", horizontal=True):
        with dpg.child_window(width=CANVAS_W+4, height=CANVAS_H+4,
                            no_scrollbar=True, border=True):
            with dpg.drawlist(width=CANVAS_W, height=CANVAS_H, tag="maze_drawlist"):
                pass
        
        btn_x = 40
        btn_y = 100
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_button(label="/\\", width=btn_x, height=btn_y, callback=lambda: move(-1, 0))
                dpg.add_button(label="\\/", width=btn_x, height=btn_y, callback=lambda: move(1,  0))
            with dpg.group(horizontal=True):
                dpg.add_button(label="<", width=btn_x, height=btn_y, callback=lambda: move(0, -1))
                dpg.add_button(label=">", width=btn_x, height=btn_y, callback=lambda: move(0,  1))

    dpg.add_separator(parent="minigame_tab")
    dpg.add_button(label="new maze", parent="minigame_tab", width=-1, height=25,
                   callback=new_maze)

    with dpg.handler_registry():
        dpg.add_key_press_handler(callback=on_key_press)
