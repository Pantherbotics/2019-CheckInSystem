ALLOWED_TIME_BETWEEN_KEY_PRESSES = 0.5 #lower = faster key presses required
CONSOLE_WINDOW_NAME = "Attendance | Gabe > everyone else" # name of the cv2 window in which attendance will be shown

## IMPORTS ##

import pythoncom, pyHook
# download pyhook at https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook
# module pyHook-1.5.1-cp37-cp37m-win32.whl
from win32gui import GetWindowText, GetForegroundWindow
import time
import os
import cv2
import numpy as np
from threading import Thread
import math

#############

## TOOL FUNCTIONS ##

def blackImg(x, y):
    return np.zeros((y, x, 3), np.uint8)
    
def textOn(img, text, pos = (0, 50), scale = 1, color = (255,255,255), lineWidth = 1, type = 2, font=cv2.FONT_HERSHEY_SIMPLEX):
    cv2.putText(img,str(text), 
                pos, 
                font, 
                scale,
                color,
                lineType = type,
                thickness = lineWidth)
    return img #is pointer
    
def activeWindowName():
    return GetWindowText(GetForegroundWindow())

def isActiveWindow():
    #True = my window is focused
    #False = my window is not focused
    n = activeWindowName()
    if n == CONSOLE_WINDOW_NAME:
        return True
    else:
        return False
    
def END_ALL_PROC():
    os._exit(1)
    
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
def asDDHHMMSS(sec):
    dd = str(math.floor( sec/(60*60*24)   ))
    hh = str(math.floor( (sec/(60*60))%24 ))
    mm = str(math.floor( (sec/60)%60      ))
    ss = str(math.floor( (sec)%60         ))
    while len(dd)<4:
        dd = "0"+dd
    if len(hh)==1:
        hh = "0"+hh
    if len(mm)==1:
        mm = "0"+mm
    if len(ss)==1:
        ss = "0"+ss
    st = dd+":"+hh+":"+mm+":"+ss
    return st
        
####################

## GUI MANAGER ##

#decides what mage is to be shown in console
ConsoleImg = blackImg(1000, 600)
cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
def CONSOLE_MANAGER():
    global ConsoleImg
    global ScannedIdQueue
    global idBuffer
    start = time.time()
    while True:
        elap = time.time()-start
        ConsoleImg = 17 * np.ones((600,1000,3), np.uint8) # reset to dark gray background
        
        ## draw bottom info bar ##
        cv2.rectangle(ConsoleImg, (0, 575), (1000, 600), (87, 166, 212), -1)
        ConsoleImg = textOn(ConsoleImg, "time since open: " + asDDHHMMSS(elap), pos = (615, 597), scale = 0.75, lineWidth = 2)
        ConsoleImg = textOn(ConsoleImg, "input: " + idBuffer, pos = (3, 597), scale = 0.75, lineWidth = 2)
        
        ## random crap ##
        ConsoleImg = textOn(ConsoleImg, ScannedIdQueue, pos=(0, 250))
        
        ## end ##
        time.sleep(0.05)
        
#shows images that above managers want to be shown & ends program on "X" button
def GUI_RENDERER():
    global ConsoleImg
    
    while True:
        if cv2.getWindowProperty(CONSOLE_WINDOW_NAME, 0)<0: #if console is closed, end program
            END_ALL_PROC()
            return None
            
        cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
        cv2.waitKey(10)

consoleMan = Thread(target = CONSOLE_MANAGER)
consoleMan.start()
scanHandler = Thread(target = GUI_RENDERER)
scanHandler.start()

#################
        
## ID SCANNER ##

ScannedIdQueue = []
def scannedID(id):
    global ScannedIdQueue
    ScannedIdQueue.insert(0, id)
    print(ScannedIdQueue)
    
idBuffer = ""
lastAdd = 0
def keyPressed(event):
    global idBuffer
    global lastAdd
    key = event.Key
    if (isInt(key)):
        if (time.time()-lastAdd)<ALLOWED_TIME_BETWEEN_KEY_PRESSES: #if current key press is soon enough after the last
            if(len(idBuffer)>=6):#if buffer is too long, restart
                #print("case 1")
                idBuffer = ""
                lastAdd = 0
            else: #if buffer is short enough to accept another digit
                #print("case 2") 
                idBuffer+=key
                lastAdd = time.time()
        else: #if took too long between presses, restart with this key
            #print("case 3")
            idBuffer = key
            lastAdd = time.time()
    else: #if key is not numeric
        if key=="Return":# if pressed enter
            if (time.time()-lastAdd)>ALLOWED_TIME_BETWEEN_KEY_PRESSES: #if took too long to press enter, start over
                #print("case 4")
                idBuffer = ""
                lastAdd = 0
            else: #if pressed enter in correct amount of time
                if(len(idBuffer)==6):#if buffer is correct length
                    #print("case 5")
                    scannedID(idBuffer)
                    idBuffer = ""
                    lastAdd = 0
                else: #if buffer is incorrect length, start over
                    #print("case 6")
                    idBuffer = ""
                    lastAdd = 0
        else: #if pressed alphabetical / symbolic key, start over
            #print("case 7")
            idBuffer = ""
            lastAdd = 0
    
    # return True to pass the event to other handlers
    return True

hm = pyHook.HookManager()
hm.KeyDown = keyPressed
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()