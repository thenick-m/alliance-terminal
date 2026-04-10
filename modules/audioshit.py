from just_playback import Playback
import threading
import time

sfx_volume = 1.0
radio = Playback()
active_sfx = []

# --- SFX ---

def play_sound(filename, volume=None, max_time=None):
    global active_sfx
    vol = sfx_volume if volume is None else volume

    #clean up finished sounds
    active_sfx[:] = [p for p in active_sfx if p.playing]

    p = Playback()
    p.load_file(filename)
    p.set_volume(vol) #TODO: fix ts not changing
    p.play()
    active_sfx.append(p)

    if max_time:
        threading.Timer(max_time/1000, p.stop).start()

    return p

# --- radio ---

def play_radio(filepath, started_at):
    global radio
    radio.stop()
    radio.load_file(filepath)
    radio.set_volume(sfx_volume)
    radio.play()
    offset = time.time() - started_at
    radio.seek(offset)

def stop_radio():
    radio.stop()

def set_volume(volume):
    global sfx_volume
    sfx_volume = volume
    radio.set_volume(volume)