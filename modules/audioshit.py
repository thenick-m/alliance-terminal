#sfx manager
from pygame import mixer

sfx_volume = 1

sfx = {}

def play_sound(filename, volume=sfx_volume, max_time=None):
    global sfx

    if filename in sfx.keys():
        sound = sfx[filename]
    else:
        sfx[filename] = mixer.Sound(filename)
        sound = sfx[filename]


    sound.set_volume(volume)
    if max_time:
        sound.play(maxtime=max_time)
    else:
        sound.play()

    return sound