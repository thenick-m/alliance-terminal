from just_playback import Playback
import threading
import time

sfx_volume = 1.0
_radio = Playback()
_active_sfx = []

# --- SFX ---

def play_sound(filename, volume=None, max_time=None):
    vol = sfx_volume if volume is None else volume

    #clean up finished sounds
    _active_sfx[:] = [p for p in _active_sfx if p.playing]

    p = Playback()
    p.load_file(filename)
    p.set_volume(vol) #TODO: fix ts not changing
    p.play()
    _active_sfx.append(p)

    if max_time:
        threading.Timer(max_time/1000, p.stop).start()

    return p

# --- radio ---

def play_radio(filepath, started_at):
    global _radio
    _radio.stop()
    _radio.load_file(filepath)
    offset = time.time() - started_at
    _radio.seek(offset)
    _radio.set_volume(sfx_volume)
    _radio.play()

def stop_radio():
    _radio.stop()

def set_volume(volume):
    global sfx_volume
    sfx_volume = volume
    _radio.set_volume(volume)