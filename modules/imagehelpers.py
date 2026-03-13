#helps with loading images and shit
from dearpygui import dearpygui as dpg
from PIL import Image
import random

tint = (250, 134, 55)

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
    tinted = Image.new("RGB", img.size, tint)
    tinted = Image.blend(Image.new("RGB", img.size, (0,0,0)), tinted, 1.0)
    
    tinted = Image.composite(tinted, Image.new("RGB", img.size, (0,0,0)), grayscale)

    tinted.putalpha(a)
    return tinted

def retroify_img(img):
    r, g, b, a = img.split()  #preserve original alpha
    
    grayscale = Image.merge("RGB", (r, g, b)).convert("L")
    tinted = Image.new("RGB", img.size, tint)
    tinted = Image.blend(Image.new("RGB", img.size, (0,0,0)), tinted, 1.0)
    
    tinted = Image.composite(tinted, Image.new("RGB", img.size, (0,0,0)), grayscale)

    tinted.putalpha(a)
    return tinted

def generate_noise(width, height, opacity=30):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            if random.randint(0, 67) == 67:  # sparse spark
                length = random.randint(0, 3)  # variable streak length
                for i in range(length):
                    if x + i < width:
                        pixels[x + i, y] = (255, 255, 255, opacity)
    
    return retroify_img(img)