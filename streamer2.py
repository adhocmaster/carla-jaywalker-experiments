import tkinter
import carla
from carla import ColorConverter as cc
import os
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import multiprocessing
import time
import random
from tkinter import *
from PIL import Image, ImageTk

#Create a window
window=Tk()

# directory

path = "logs/stream/"

if not os.path.exists(path):
    os.makedirs(path)

imW = 1000
imH = 562
def plot():    #Function to create the base plot, make sure to make global the lines, axes, canvas and any part that you would want to update later

    print("plot")
    # global line,ax,canvas
    global canvas
    global window
    canvas = Canvas(window, width = 1000, height = 1000)
    canvas.pack()
    
    # img = ImageTk.PhotoImage(file=f'{path}/225196.png')
    img = ImageTk.PhotoImage(file=f'{path}/s2.jpeg')
    canvas.create_image(20, 20, anchor=NW, image=img)
    canvas.image = img
    pass

# canvas = Canvas(window, width = 1000, height = 1000)
# canvas.pack()


# img = ImageTk.PhotoImage(file=f'{path}/225196.png')
# # img = ImageTk.PhotoImage(file=f'{path}/s2.jpeg')
# canvas.create_image(20, 20, anchor=NW, image=img)

plot()
window.mainloop()


