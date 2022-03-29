import tkinter
import carla
from carla import ColorConverter as cc
import os
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import multiprocessing
import queue
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

def process_img_wrapper(q):


    def process_img(image):
        nonlocal q
        print("process img called")
        image.convert(cc.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        # print(type(image.raw_data))
        # image.save_to_disk(f'{path}/image.frame_number')
        # plt.imshow(array)
        im = Image.fromarray(array)
        im = im.crop((imW * 0.2, 0, imW * 0.8, imH))
        # im.save(f'{path}/{image.frame_number}.png')
        q.put(im)
        print(f"process_img qsize {q.qsize()}")

    return process_img



def main():
    #Create a queue to share data between process
    global q
    q = multiprocessing.Queue()

    #Create and start the simulation process
    simulate=multiprocessing.Process(None,simulation,args=(q,))
    simulate.start()

    #Create the base plot
    plot()

    #Call a function to update the plot when there is new data
    updateplot(q)

    window.mainloop()
    # simulate.join()
    print('Done')

def plot():    #Function to create the base plot, make sure to make global the lines, axes, canvas and any part that you would want to update later

    # global line,ax,canvas
    global canvas, window, imW, imH
    canvas = Canvas(window, width = imH, height = imH) # squared
    canvas.pack()

    
    # img = ImageTk.PhotoImage(file=f'{path}/225196.png')
    # img = ImageTk.PhotoImage(file=f'{path}/s2.jpeg')
    # canvas.create_image(20, 20, anchor=NW, image=img)
    # canvas.image = img
    pass

def updateplot(q):
    global window, canvas
    # print(f"updateplot queue size {q.qsize()}")
    try:       #Try to check if there is data in the queue
        result=q.get_nowait()
        # print("printing the image")

        # if result !='Q':
        #      print(result)
        #          #here get crazy with the plotting, you have access to all the global variables that you defined in the plot function, and have the data that the simulation sent.
        #      line.set_ydata([1,result,10])
        #      ax.draw_artist(line)
        #      canvas.draw()
        #      window.after(500,updateplot,q)
        # else:
        #      print('done')
        img = ImageTk.PhotoImage(result)
        # img = ImageTk.PhotoImage(file=f'{path}/225196.png')
        canvas.create_image(0, 0, anchor=NW, image=img)
        canvas.image = img
        # imgLabel = Label(image=img)
        
        # imgLabel.place(x=50, y=50)
    except queue.Empty:
        # print("empty")
        window.after(100, updateplot, q)
        return
    except:
        # something else happened with queue. shut down.
        print("Shutting down update plot")
        return
    window.after(100, updateplot, q)


def simulation(q):
    # iterations = xrange(100)
    # for i in iterations:
    #     if not i % 10:
    #         time.sleep(1)
    #             #here send any data you want to send to the other process, can be any pickable object
    #         q.put(random.randint(1,10))
    # q.put('Q')


    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(5.0)

    world = client.get_world()
    spectator = world.get_actors().filter('spectator')[0]

    bp_library = world.get_blueprint_library()
    camera_bp = bp_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', f'{imW}')
    camera_bp.set_attribute('image_size_y', f'{imH}')
    camera_bp.set_attribute('sensor_tick', '0.15')

    camera = world.spawn_actor(camera_bp, spectator.get_transform())
    process_img = process_img_wrapper(q)
    camera.listen(process_img)
    print("started simulation")

    try:
        while True:
            world.wait_for_tick()
    except KeyboardInterrupt:
        camera.destroy
        q.close()

if __name__ == '__main__':
    main()