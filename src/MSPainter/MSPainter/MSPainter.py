###############################################
# Imports
###############################################

import sys
import numpy as np
from PIL import Image
import win32api
import win32.lib.win32con as win32con
import time
from pynput.mouse import Listener
import win32gui
from threading import Timer
import os
import math
from pynput import mouse
import os.path

###############################################
# GLOBALS
###############################################

prompts = ["Click the top-left color icon in Paint",
           "Click the bottom-right color icon in Paint",
           "Click the top-left of the canvas in Paint"]
step = 0
top_left_color_x, top_left_color_y = (0, 0)
bottom_right_color_x, bottom_right_color_y = (0, 0)
top_left_canvas_x, top_left_canvas_y = (0, 0)

###############################################
# class perpetualTimer()
###############################################

class perpetualTimer():

   def __init__(self, t, hFunction):
      self.t = t
      self.hFunction = hFunction
      self.thread = Timer(self.t, self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t, self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def stop(self):
      self.thread.cancel()

###############################################
# on_click()
###############################################

def on_click(x, y, button, pressed):
    global step, top_left_color_x, top_left_color_y, bottom_right_color_x, bottom_right_color_y, top_left_canvas_x, top_left_canvas_y

    if(pressed):
        if(button == mouse.Button.left):
            if (step == 0):
                (top_left_color_x, top_left_color_y) = (x, y)
                step += 1
                print(prompts[step])
            elif (step == 1):
                (bottom_right_color_x, bottom_right_color_y) = (x, y)
                step += 1
                print(prompts[step])
            elif (step == 2):
                (top_left_canvas_x, top_left_canvas_y) = (x, y)
                step += 1
        elif(button == mouse.Button.right):
            os._exit(2)

###############################################
# get_rgb()
###############################################

def get_rgb(pixel):
    return (pixel & 255, (pixel >> 8) & 255, (pixel >> 16) & 255)

###############################################
# get_closest_color()
###############################################

def get_closest_color(rgb_array, palette):
    (r1, g1, b1) = (rgb_array[0], rgb_array[1], rgb_array[2])

    closest_color = pow(255, 2) + pow(255, 2) + pow(255, 2)
    closest_color_index = 0

    for i in range(0, len(palette)):
        (_, _, (r2, g2, b2)) = palette[i]
        d = pow(((r2-r1)), 2) + pow(((g2-g1)), 2) + pow(((b2-b1)), 2)
        if (d < closest_color):
            closest_color = d
            closest_color_index = i

    return closest_color_index

###############################################
# generate_image_array()
###############################################

def generate_image_array(palette, img_path):
    print("Generating image array, please wait..")
    img = Image.open(img_path)
   
    original_array = np.array(img)
    new_array = np.ndarray((img.width, img.height), np.int32)

    last_pc = 0
    for x in range(0, img.width - 1):
        current_pc = int((x / img.width) * 100)
        if (current_pc != last_pc):
            print(f"{current_pc}%")
            last_pc = current_pc
        for y in range(0, img.height-1):
            new_array[x, y] = get_closest_color(original_array[y,x], palette)

    return new_array

###############################################
# main()
###############################################

def main(image_path):
    global top_left_canvas_x, top_left_canvas_y

    print(prompts[step])

    with Listener(on_click=on_click) as listener:
        global t

        def time_out():
            global step
            if (step > 2):
                t.stop()
                listener.stop()                

        t = perpetualTimer(1, time_out)
        t.start()
        listener.join()

    # Get the horizontal offset between the 10 columns of colours
    horizontal_color_interval = ((bottom_right_color_x - top_left_color_x) / 9)
    # Get the vertical offset between the 2 rows of colours
    vertical_color_interval = (bottom_right_color_y - top_left_color_y)

    palette = []
    x_float = float(top_left_color_x);
    while (x_float <= bottom_right_color_x):
        x = int(x_float)
        y = top_left_color_y;

        win32api.SetCursorPos((x, y))
        pixel = win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), x , y)
        palette.append((x, y, get_rgb(pixel)))
        
        y += vertical_color_interval

        win32api.SetCursorPos((x, y))
        pixel = win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), x , y)
        palette.append((x, y, get_rgb(pixel)))

        x_float += horizontal_color_interval

    image_ids = generate_image_array(palette, image_path)

    (width, height) = image_ids.shape
    for i in range(0, len(palette)):
        # Skip colour 1, since it's white and the canvas should already be this colour
        if (i==1):
            continue;

        (color_x, color_y, (_, _, _)) = palette[i]
        win32api.SetCursorPos((color_x, color_y))
        time.sleep(0.25)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, color_x, color_y, 0, 0)
        time.sleep(0.25)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, color_x, color_y, 0, 0)
        time.sleep(0.25)
        for x in range(0, width):
            for y in range(0, height):
                if (image_ids[(x, y)] == i):
                    win32api.SetCursorPos((top_left_canvas_x + x, top_left_canvas_y + y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, top_left_canvas_x + x, top_left_canvas_y + y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, top_left_canvas_x + x, top_left_canvas_y + y, 0, 0)
                    time.sleep(0.01)

    os._exit(0)

###############################################
# Startup
###############################################

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("Usage: Python MSPainter.py IMAGE_FILE")
        os._exit(1)

    if (not os.path.isfile(sys.argv[1])):
        print("Cannot find file {argv[1]}")
        os._exit(1)

    main(sys.argv[1])