from dearpygui import dearpygui as dpg
import random
import threading

from modules import audioshit as sound
from modules import requesthandler4000 as rq
from modules import state
from modules import imagehelpers
from modules.state import *

import yt_dlp

def download_audio(url, filename):
    ydl_opts = {
        'format': 'worstaudio',
        'outtmpl': savepath(f"other/radio/{filename}.mp3"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
        }],
        'quiet': True,
        'ffmpeg_location': locally("other")
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def radio():
    def activate_radio():
        print(rq.get_radio_state())

    dpg.add_button(label="connect to radio", callback=activate_radio)