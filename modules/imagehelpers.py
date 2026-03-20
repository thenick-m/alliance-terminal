#helps with loading images and shit
from dearpygui import dearpygui as dpg
from PIL import Image
import numpy as np

#other
import time
import threading

from modules import state

def load_pil_image(tag, img):
    img = img.convert("RGBA")
    width, height = img.size
    data = [x/255.0 for x in img.tobytes()]
    
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=tag)

def retroify(image_path):
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()  #preserve original alpha
    
    grayscale = Image.merge("RGB", (r, g, b)).convert("L")
    tinted = Image.new("RGB", img.size, state.color4)
    tinted = Image.blend(Image.new("RGB", img.size, (0,0,0)), tinted, 1.0)
    
    tinted = Image.composite(tinted, Image.new("RGB", img.size, (0,0,0)), grayscale)

    tinted.putalpha(a)
    return tinted

#converted render to numpy in v0.1.5
def generate_retro_boi(width, height, opacity=45):
    img = np.zeros((height, width, 4), dtype=np.uint8)

    #noise
    streak_length = 15
    mask = np.random.randint(0, 600, (height, width)) == 0
    for dx in range(streak_length):
        shifted = np.roll(mask, dx, axis=1)
        img[shifted, 0] = state.color4[0]
        img[shifted, 1] = state.color4[1]
        img[shifted, 2] = state.color4[2]
        img[shifted, 3] = opacity

    #scanlines
    img[::2, :, 0] = np.clip(img[::2, :, 0].astype(int) - 60, 0, 255)
    img[::2, :, 1] = np.clip(img[::2, :, 1].astype(int) - 60, 0, 255)
    img[::2, :, 2] = np.clip(img[::2, :, 2].astype(int) - 60, 0, 255)

    r, g, b = state.color1
    img[::2, :] = [r, g, b, 100]

    #glitch line
    scan_line_probability = 0.3
    if np.random.default_rng().random() <= scan_line_probability:
        gy = np.random.randint(0, height)
        img[gy, :] = list(state.color4) + [np.random.randint(20, 50)]

    return Image.fromarray(img, 'RGBA')

def channel_switch(duration=0.2):
    width, height = state.WIDTH, state.HEIGHT
    c = state.color4

    img = np.zeros((height, width, 4), dtype=np.uint8)
    img[:, :] = [c[0], c[1], c[2], 230]
    dpg.set_value("noise_texture", [x / 255.0 for x in Image.fromarray(img, "RGBA").tobytes()])

    def _run():
        rng = np.random.default_rng()
        t_start = time.perf_counter()

        while True:
            t = (time.perf_counter() - t_start) / duration
            if t >= 1.0:
                dpg.set_value("noise_texture", [0.0] * (width * height * 4))
                break

            ease = 1.0 - t
            img = np.zeros((height, width, 4), dtype=np.uint8)

            if t < 0.2:
                flash_alpha = int(230 * (1.0 - t / 0.2))
                img[:, :] = [c[0], c[1], c[2], flash_alpha]

            #horizontal tear bands (sync-loss lines)
            n_tears = max(1, int(7 * ease))
            for _ in range(n_tears):
                y = int(rng.integers(0, height))
                h = int(rng.integers(2, max(3, int(18 * ease))))
                alpha = int(200 * ease)
                img[y : y + h, :] = [c[0], c[1], c[2], alpha]

            #per-row horizontal displacement
            max_shift = int(width * 0.18 * ease)
            if max_shift > 1:
                for y in range(height):
                    if rng.random() < 0.30 * ease:
                        shift = int(rng.integers(-max_shift, max_shift))
                        img[y] = np.roll(img[y], shift, axis=0)

            #dense noise burst
            density = max(8, int(180 * ease))
            mask = rng.integers(0, density, (height, width)) == 0
            streak = 30
            noise_alpha = int(200 * ease)
            for dx in range(streak):
                s = np.roll(mask, dx, axis=1)
                img[s, 0] = c[0]
                img[s, 1] = c[1]
                img[s, 2] = c[2]
                img[s, 3] = noise_alpha

            #scanline darkening still present
            img[::2, :, 3] = np.clip(img[::2, :, 3].astype(int) - 50, 0, 255)

            data = [x / 255.0 for x in Image.fromarray(img, "RGBA").tobytes()]
            dpg.set_value("noise_texture", data)


    threading.Thread(target=_run, daemon=True).start()