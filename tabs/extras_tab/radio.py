from dearpygui import dearpygui as dpg
import random
import threading

from modules import audioshit as sound
from modules import requesthandler4000 as rq
from modules import state
from modules import imagehelpers
from modules.state import *

import yt_dlp

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'worstaudio',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
        }],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def radio():
    pass