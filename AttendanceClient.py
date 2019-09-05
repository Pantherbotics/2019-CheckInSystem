ALLOWED_TIME_BETWEEN_KEY_PRESSES = 0.5 #lower = faster key presses required
CONSOLE_WINDOW_NAME = "Gabe is the best tbh" # name of the cv2 window in which attendance will be shown
NOTIFIER_WINDOW_NAME = "Gabe's cool notifier" # name of the cv2 window in which notifications (Welcome; Goodbye) will be shown

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

def whichActiveWindow():
    # 0 = not related to this program (i.e. google chrome)
    # 1 = this program's main console
    # 2 = this program's notification box
    n = activeWindowName()
    if n == CONSOLE_WINDOW_NAME:
        return 1
    elif n == NOTIFIER_WINDOW_NAME:
        return 2
    else:
        return 0
    
def END_ALL_PROC():
    os._exit(1)
    
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
####################

## GUI MANAGER ##

#decides what mage is to be shown in console
ConsoleImg = blackImg(1000, 600)
cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
def CONSOLE_MANAGER():
    global ConsoleImg
    start = time.time()
    while True:
        ConsoleImg = blackImg(1000, 600)# reset to black
        elap = time.time()-start
        ConsoleImg = textOn(ConsoleImg, elap)
        time.sleep(0.01)
        
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