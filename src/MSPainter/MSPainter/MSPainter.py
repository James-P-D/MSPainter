import numpy as np
from PIL import Image # pip install pillow
import win32api # pip install pywin32
import win32.lib.win32con as win32con
import time
from pynput.mouse import Listener
import win32gui
from threading import Timer
import os
import math
prompts = ["Click the top-left color icon in Paint",
           "Click the bottom-right color icon in Paint",
           "Click the top-left of the canvas in Paint",
           "Click the bottom-right of the canvas in Paint"]
step = 0
top_left_color_x, top_left_color_y = (0, 0)
bottom_right_color_x, bottom_right_color_y = (0, 0)
top_left_canvas_x, top_left_canvas_y = (0, 0)
bottom_right_canvas_x, bottom_right_canvas_y = (0, 0)


def on_click(x, y, button, pressed):
    global step, top_left_color_x, top_left_color_y, bottom_right_color_x, bottom_right_color_y, top_left_canvas_x, top_left_canvas_y, bottom_left_canvas_x, bottom_right_canvas_y

    if(pressed):
        #print(x, y, button, pressed)
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
            print(prompts[step])
        elif(step == 3):
            (bottom_right_canvas_x, bottom_right_canvas_y) = (x, y)
            step += 1

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def stop(self):
      self.thread.cancel()

def get_rgb(pixel):
    return ((pixel >> 16) & 255, (pixel >> 8) & 255, pixel & 255)

def get_closest_color(rgb_array, palette):
    (r1, g1, b1) = (rgb_array[0], rgb_array[1], rgb_array[2])

    closest_color = 999999 # TODO: set to some kind of int.MAX?
    closest_color_index = 0

    for i in range(0, len(palette)):
        (_, _, (r2, g2, b2)) = palette[i]
        d = math.sqrt(((r2-r1)*0.3)**2 + ((g2-g1)*0.59)**2 + ((b2-b1)*0.11)**2)
        if (d < closest_color):
            closest_color = d
            closest_color_index = i

    return closest_color_index

def generate_image_array(palette, img_path):
    img = Image.open(img_path)
   
    original_array = np.array(img) # 640x480x4 array
    new_array = np.ndarray((img.width, img.height), np.int32)

    for x in range(0, img.width-1):
        print(f"{x} of {img.width-1}")
        for y in range(0, img.height-1):
            new_array[x, y] = get_closest_color(original_array[y,x], palette)

    return new_array

def main():
    global top_left_canvas_x, top_left_canvas_y

    print(prompts[step])

    with Listener(on_click=on_click) as listener:
        global t

        def time_out():
            global step
            if (step > 3):
                t.stop()
                listener.stop()                

        t = perpetualTimer(1, time_out)
        t.start()
        listener.join()

    horizontal_color_interval = ((bottom_right_color_x - top_left_color_x) / 9)
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

    image_ids = generate_image_array(palette, r'C:\Users\jdorr\Desktop\monochrome.jpg')

    print(image_ids.shape)
    (width, height) = image_ids.shape
    for i in range(0, len(palette)):
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
                    time.sleep(0.1)


    os._exit(0)

###############################################
# Startup
###############################################

if __name__ == "__main__":
    main()