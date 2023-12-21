"""
.. py:module::  : RaspberryPiCar_remote 

* Filename      : RaspberryPiCar_remote.py
* Description   : A module to remotely control the RaspberryPiCar,
                   display the camera data (including object recognition) on
                   the PC used for the remote control and to store images  
                   to enable creating a data set for training an AI. 
* Author        : Joanna Rieger
* Project work  : "Entwicklung eines Modells zur Objekterkennung von 
                   Straßenschildern für ein ferngesteuertes Roboterauto"
* E-mail        : joanna.rieger@stud.hshl.de
"""

################################################################################
#################################    SOURCES    ################################
################################################################################
# https://docs.sunfounder.com/_/downloads/picar-v/en/latest/pdf/
# https://github.com/sunfounder/SunFounder_PiCar-V/tree/V3.0

# https://www.youtube.com/watch?v=v0ssiOY6cfg&t=401s
# https://colab.research.google.com/github/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Train_TFLite2_Object_Detction_Model.ipynb
# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/deploy_guides/Raspberry_Pi_Guide.md
# https://github.com/HumanSignal/labelImg/releases
# https://coral.ai/docs/accelerator/get-started/#3-run-a-model-on-the-edge-tpu

# https://zeromq.org/
# https://github.com/jeffbass/imagezmq


################################################################################
#################################    IMPORTS    ################################
################################################################################
import zmq
import msgpack
import time
import numpy as np
import threading
import imagezmq                            
import cv2
import tkinter 
import math
import keyboard                             
from PIL import Image, ImageTk


#################################################################################
#################################     SET UP     ################################
#################################################################################   
#----------------------------------------------------------------------           
# > Configuration of the GUI 
# > Setting up ZeroMQ and imageZMQ for the exchange of data
#----------------------------------------------------------------------
root = tkinter.Tk()
root.config(bg="#F0F0F0", borderwidth=200)
root.title("RaspberryPiCar")
lbl = tkinter.Label(root, text="\n    Waiting for the    \n    connection to the    \n    RaspberryPiCar's    \n    camera ...    \n", font= "Arial 20")
lbl.pack(side="bottom", fill="both", expand="yes")
                           
command = {"speed": 0, "angle": 0}  
context = zmq.Context()                                                                                                                                                                 
socket = context.socket(zmq.PAIR)        
# --- HOME ---                                   
socket.connect("tcp://192.168.178.40:5556")                         
image_hub = imagezmq.ImageHub(open_port="tcp://192.168.178.40:6665", REQ_REP=False)  
# --- HSHL - Gäste ---  
# socket.connect("tcp://192.168.200.56:5556") 
# image_hub = imagezmq.ImageHub(open_port="tcp://192.168.200.56:6665", REQ_REP=False)                                      



################################################################################
################################    FUNCTIONS    ###############################
################################################################################ 
def listen(label: tkinter.Label):
    """ 
    The function receives an image-array from the Raspberry Pi, converts it from 
    BGR to RGB and displays the image-array as an image in the GUI.
        > Image-arrays are processed in a while-loop
            > Livestream of the camera in the GUI
        > If the keyboard key "p" is pressed the last received 
           image-array is saved as an image (.jpg).

    Args:
        label (tkinter.Label): label element to place image in GUI 
    """
    
    img_counter = 1
    path = "E:\VSCode_Projects\RaspberryPiCar\AI_Pictures\AI_RaspberryPiCar_"
    
    while True:
        rpi_name, image = image_hub.recv_image()                            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(image_rgb))
        label.configure(image=img)
        label.image = img
        
        if keyboard.is_pressed("p"):
            time.sleep(0.1)
            img_name = "{}.jpg".format(img_counter)
            cv2.imwrite(str(path) + str(img_name), image) 
            img_counter += 1 
            print("{} saved!".format(img_name)) 
        
def send_keyboard_input():
    """
    The function receives the keyboard input from the keys "w", "a", "s", 
    "d", "q", "1", "2" and "3". According to the pressed keys the values of 
    the variables "spd", "ngl" and "fctr" are changed. Using these variables 
    the values "speed" and "angle" in the dictionary "command" are updated 
    and send to the Raspberry Pi. 
     
    * spd = the given value determines the speed of the car                    
    * fctr = factor to calculate the speed
    * ngl = values for the steering angle 45 > left ("a"), 315 > right ("d")
    
    > If the keyboard key "q" is pressed the function quit() is called.     
        > Closes the GUI-window
    """
    spd = 0
    ngl = 0 
    fctr = 1
    
    while True:
        if keyboard.is_pressed("1"):
            fctr = 1
        elif keyboard.is_pressed("2"):
            fctr = 1.5
        elif keyboard.is_pressed("3"):
            fctr = 2  
             
        if keyboard.is_pressed("w"):
            spd = fctr * -30
        elif keyboard.is_pressed("s"):
            spd = fctr * 30
        else: 
            spd = 0
            
        if keyboard.is_pressed("d"):
            ngl = 315
        elif keyboard.is_pressed("a"):
            ngl = 45
        else: 
            ngl = 0
        
        if keyboard.is_pressed("q"):
            quit()
            
        command = {"speed": spd, "angle": ngl}
        socket.send(msgpack.packb(command)) 
                                                
def quit():
    """
    Function to close the GUI-window.
    """
    print("GUI - Quit")  
    root.destroy()



t1 = threading.Thread(target=listen, args=(lbl, ))
t2 = threading.Thread(target=send_keyboard_input)
t1.start()   
t2.start()
                
root.protocol("WM_DELETE_WINDOW", quit)
root.mainloop()