from http import client
import tkinter
import carla
from carla import ColorConverter as cc
import os
import numpy as np
import time

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import multiprocessing
import queue
import time
import random
from tkinter import *
from PIL import Image, ImageTk
import imageio

import click

#defaul config
ghost = '127.0.0.1'
gport = 2000
gTimeout = 15.0

#Create a window
window=Tk()
images = []

# directory

path = "logs/stream/"

if not os.path.exists(path):
    os.makedirs(path)

imW = 1000
imH = 562
lastTime = time.time()

def process_img_wrapper(q, resetCameraQ):
    

    def process_img(image):
        nonlocal q, resetCameraQ
        fname = 'output/%.6d.jpg' % image.frame
        image.save_to_disk(fname)
   
        images.append(imageio.imread(fname))
        
        # print("process img called")
        # image.convert(cc.Raw)
        # array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        # array = np.reshape(array, (image.height, image.width, 4))
        # array = array[:, :, :3]
        # array = array[:, :, ::-1]
        # im = Image.fromarray(array)
        # im = im.crop((imW * 0.2, 0, imW * 0.8, imH))
        # # im.save(f'{path}/{image.frame_number}.png')
        # q.put(im)
        # print(f"process_img qsize {q.qsize()}")

    return process_img



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

def updateplot(q, resetCameraQ):
    global window, canvas, lastTime
    return
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
        lastTime = time.time()

    except queue.Empty:
        # print("empty")
        resetTime = .2
        if (time.time() - lastTime) > resetTime:
            lastTime = time.time()
            resetCameraQ.put(True)
            window.after(int(resetTime * 1000), updateplot, q, resetCameraQ)
        else:
            window.after(100, updateplot, q, resetCameraQ)
        return
    except:
        # something else happened with queue. shut down.
        print("Shutting down update plot")
        return
    window.after(100, updateplot, q, resetCameraQ)


def simulation(q, resetCameraQ, host, port):
    # iterations = xrange(100)
    # for i in iterations:
    #     if not i % 10:
    #         time.sleep(1)
    #             #here send any data you want to send to the other process, can be any pickable object
    #         q.put(random.randint(1,10))
    # q.put('Q')
    global ghost, gport

    ghost = host
    gport = port

    world, camera = initCamera(q, resetCameraQ)

    print("started streaming")

    while True:
        try:
            world, camera = simulatorWait(world, camera, q, resetCameraQ)
        except KeyboardInterrupt:
            imageio.mimsave(f'gifs/{time.time()}', images)
            safeDeleteCamera(world)
            q.close()
            resetCameraQ.close()
            return
        except RuntimeError as e:
            print(f"runtime error, recreating world and camera")
            print(e)
            safeDeleteCamera(world)
            world, camera = initCamera(q, resetCameraQ)


def safeDeleteCamera(world, camera):
    # delete only if the camera exists
    if world.get_snapshot().find(camera.id) is not None:
        camera.stop()
        camera.destroy()

    pass

def getExistingSepectatorCamera(world):
    spectator = world.get_actors().filter('spectator')[0]
    cameras = world.get_actors().filter('sensor.camera.rgb')
    return cameras[len(cameras)-1]
    for camera in cameras:
        if camera.parent.id == spectator.id:
            print("found existing camera with the spectator")
            return camera
    return None


def getSepectatorCamera(world):
    print(world.get_actors())
    spectator = world.get_actors().filter('sensor.camera.rgb')[0]

    # check if a camera already exists.

    existingCamera = getExistingSepectatorCamera(world)

    if existingCamera is not None:
        return existingCamera
    

    spectator = world.get_actors().filter('spectator')[0]

    print(f"fetching blueprint_library")
    bp_library = world.get_blueprint_library()
    camera_bp = bp_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', f'{imW}')
    camera_bp.set_attribute('image_size_y', f'{imH}')
    camera_bp.set_attribute('sensor_tick', '0.2')

    print(f"spawning camera")

    transform = carla.Transform() # 0,0,0

    camera = world.spawn_actor(camera_bp, transform, attach_to=spectator)

    return camera



def initCamera(q, resetCameraQ):

    global ghost, gport, gTimeout

    print(f"creating camera")
    
    # client = carla.Client('127.0.0.1', 2000)

    print(f"connecting to remote: {ghost}:{gport}")
    client = carla.Client(ghost, gport)
    client.set_timeout(gTimeout)
    print(f"connected to remote: {ghost}:{gport}")

    print(f"fetching world and spectator")
    world = client.get_world()

    # spectator = world.get_actors().filter('spectator')[0]

    # print(f"fetching blueprint_library")
    # bp_library = world.get_blueprint_library()
    # camera_bp = bp_library.find('sensor.camera.rgb')
    # camera_bp.set_attribute('image_size_x', f'{imW}')
    # camera_bp.set_attribute('image_size_y', f'{imH}')
    # camera_bp.set_attribute('sensor_tick', '0.5')

    # print(f"spawning camera")

    # camera = world.spawn_actor(camera_bp, spectator.get_transform())

    camera = getSepectatorCamera(world)

    process_img = process_img_wrapper(q, resetCameraQ)

    print(f"attaching camera listener")
    camera.listen(process_img)
    print(f"new camera created with id {camera.id}")

    return world, camera


def simulatorWait(world, camera, q, resetCameraQ):
    # print(f"simulatorWait")
    world.wait_for_tick()

    # existingCamera = world.get_snapshot().find(camera.id)
    existingCamera = world.get_actors().find(camera.id)
    if existingCamera is None or existingCamera.type_id != camera.type_id:
        world, camera = initCamera(q, resetCameraQ)
        # return world
    
    return world, camera


    # result=resetCameraQ.get_nowait() 
    # # means camera no longder exists
    # safeDeleteCamera(world)
    # world, camera = initCamera(q, resetCameraQ)
    # try:
    #     result=resetCameraQ.get_nowait()
    #     # means camera no longder exists
    #     safeDeleteCamera(world)
    #     world, camera = initCamera(q, resetCameraQ)
    # except queue.Empty:
    #     simulatorWait(world, camera, q, resetCameraQ)
    #     pass

@click.command()

@click.option(
    '-h', '--host',
    metavar='ip address',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)',
    prompt=True
    )
@click.option(
    '-p', '--port',
    metavar='number',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)', 
    prompt=True
    )
@click.option(
    '-t', '--timeout',
    metavar='number',
    default=5.0,
    type=int,
    help='Client timeout(default: 5.0)', 
    prompt=True
    )

def main(host, port, timeout):
    #Create a queue to share data between process
    global q, ghost, gport, gTimeout

    ghost = host
    gport = port
    gTimeout = timeout
    q = multiprocessing.Queue()
    resetCameraQ = multiprocessing.Queue()

    #Create and start the simulation process
    simulate=multiprocessing.Process(None,simulation,args=(q, resetCameraQ, host, port))
    simulate.start()

    print(f"connecting to remote. Waiting 20 seconds to start streaming")
    time.sleep(20)

    #Create the base plot
    plot()

    #Call a function to update the plot when there is new data
    updateplot(q, resetCameraQ)

    window.mainloop()
    # simulate.join()
    print('Done')

if __name__ == '__main__':
    main()