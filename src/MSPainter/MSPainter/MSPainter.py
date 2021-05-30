import numpy as np
from PIL import Image # pip install pillow
import win32api # pip install pywin32
import time
from pynput.mouse import Listener
import win32gui
from threading import Timer
import os

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

def main():

    img = Image.open(r'C:\Users\jdorr\Desktop\monochrome.jpg')
   
    arr = np.array(img) # 640x480x4 array
    #arr2 = np.array(img.width, img.height, np.int32)

    for x in range(0, img.width):
        for y in range(0, img.height):
            print(arr[x,y])

    print(prompts[step])

    with Listener(on_click=on_click) as listener:
        global t

        def time_out():
            global step
            if (step > 3):
                t.stop()
                listener.stop()                

        #Timer(10, time_out).start()
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
        palette.append((x, y, (pixel >> 16) & 255, (pixel >> 8) & 255, pixel & 255))
        
        y += vertical_color_interval

        win32api.SetCursorPos((x, y))
        pixel = win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), x , y)
        palette.append((x, y, (pixel >> 16) & 255, (pixel >> 8) & 255, pixel & 255))

        x_float += horizontal_color_interval


    os._exit(0)

###############################################
# Startup
###############################################

if __name__ == "__main__":
    main()