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
import win32api
import keyboard

#############

## TOOL FUNCTIONS ##

def mouse1down():   
    return win32api.GetKeyState(0x01) < 0

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
    
def brighten(img, factor):
    overlay = img.copy()
    height, width = img.shape[:2]
    cv2.rectangle(overlay, (0, 0), (width, height), (255, 255, 255), -1)  # A filled rectangle
    img = cv2.addWeighted(overlay, factor, img, 1 - factor, 0)
    return img

def rightArrow(img, clr=(255, 255, 255)):
    height, width = img.shape[:2]
    ms = (width-50, int(height/2)) #middle start
    me = (width-10, int(height/2)) #middle end
    ts = (ms[0]+20, ms[1]-15) #top start
    te = (me[0]+0, me[1]+0) #top end
    bs = (ms[0]+20, ms[1]+15) #bottom start
    be = (me[0]+0, me[1]+0) #bottom end
    img = cv2.line(img, ms, me, clr, 3)
    img = cv2.line(img, ts, te, clr, 3)
    img = cv2.line(img, bs, be, clr, 3)
    img = textOn(img, "key", scale = 0.5, pos=(width-60, me[1]-15), color = clr)
    img = textOn(img, "arrow", scale = 0.5, pos=(width-60, me[1]-30), color = clr)
    return img

def leftArrow(img, clr=(255, 255, 255)):
    height, width = img.shape[:2]
    ms = (50, int(height/2)) #middle start
    me = (10, int(height/2)) #middle end
    ts = (ms[0]-20, ms[1]-15) #top start
    te = (me[0]-0, me[1]+0) #top end
    bs = (ms[0]-20, ms[1]+15) #bottom start
    be = (me[0]-0, me[1]+0) #bottom end
    img = cv2.line(img, ms, me, clr, 3)
    img = cv2.line(img, ts, te, clr, 3)
    img = cv2.line(img, bs, be, clr, 3)
    img = textOn(img, "key", scale = 0.5, pos=(40, me[1]-15), color = clr)
    img = textOn(img, "arrow", scale = 0.5, pos=(25, me[1]-30), color = clr)
    return img

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
EventQueue = []
curEvent = ""
def EventHandler():
    global EventQueue
    global curEvent
    while True:
        while len(EventQueue)==0:
            time.sleep(0.01)
        cmd = EventQueue[len(EventQueue)-1]
        curEvent = cmd
        cmdTyp, cmdVal = cmd.split(":")
        curEvent = cmdTyp
        if cmdTyp == "scanned":
            curEvent = "ID input: " + cmdVal
            time.sleep(1)
            EventQueue.remove(cmd)
        else:
            curEvent = "unknown command: " + cmd
            time.sleep(1)
            EventQueue.remove(cmd)
        curEvent = ""

#decides what mage is to be shown in console
ConsoleImg = blackImg(1000, 600)
cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
lastConIsActive = True
conActiveSwitchedAt = time.time()
ActivePage = 0
page_count = 3 #+1 for debug
page_change_rate = 0.2
last_page_change = 0
isLoadingConsole = False
lastIdBuffer = ""
def CONSOLE_MANAGER():
    global ConsoleImg
    global idBuffer
    global lastIdBuffer
    global ActivePage
    global last_page_change
    global page_change_rate
    global isLoadingConsole
    global lastConIsActive
    global conActiveSwitchedAt
    global EventQueue
    global curEvent
    global lastAdd
    start = time.time()
    while True:
        elap = time.time()-start
        isLoadingConsole = True #prevent GUI_RENDERER from loading imcomplete image
        ConsoleImg = 17 * np.ones((600,1000,3), np.uint8) # reset to dark gray background
        
        if ActivePage == 0:
            ConsoleImg = textOn(ConsoleImg, "display people currently here")
        elif ActivePage == 1:
            ConsoleImg = textOn(ConsoleImg, "have buttons for various actions")
        elif ActivePage == 2:
            ConsoleImg = textOn(ConsoleImg, "show event queue")            
        else: #default
            ConsoleImg = textOn(ConsoleImg, "you shouldn't be seeing this")
            ConsoleImg = textOn(ConsoleImg, EventQueue, pos=(0, 250))
            ConsoleImg = textOn(ConsoleImg, "active: " + str(isActiveWindow()), pos=(0, 300))
            ConsoleImg = textOn(ConsoleImg, "mouse : " + str(mouse1down()), pos=(0, 350))
            ConsoleImg = textOn(ConsoleImg, "page  : " + str(ActivePage), pos=(0, 400))
        ##isActiveWindow##
        if lastConIsActive!=isActiveWindow():
            conActiveSwitchedAt = time.time()
            lastConIsActive = not lastConIsActive
        if not lastConIsActive:
            a = (time.time() - conActiveSwitchedAt)*2
            if a>0.5:
                a=0.5
            ConsoleImg = brighten(ConsoleImg, a)
        else:
            a = (time.time() - conActiveSwitchedAt)*2
            if a>0.5:
                a=0.5
            ConsoleImg = brighten(ConsoleImg, 0.5-a)
            
        ## draw bottom info bar ##
        myIdbuffer = idBuffer
        if (time.time()-lastAdd) > ALLOWED_TIME_BETWEEN_KEY_PRESSES:
            myIdbuffer = ""
        cv2.rectangle(ConsoleImg, (0, 575), (1000, 600), (87, 166, 212), -1)
        ConsoleImg = textOn(ConsoleImg, "time since open: " + asDDHHMMSS(elap), pos = (615, 595), scale = 0.75, lineWidth = 2)
        ConsoleImg = textOn(ConsoleImg, "input: " + myIdbuffer, pos = (3, 595), scale = 0.75, lineWidth = 2)
        
        ##draw top info bar ##
        if curEvent!="":
            cv2.rectangle(ConsoleImg, (0, 0), (1000, 20), (230, 230, 230), -1)
            textsize = cv2.getTextSize(curEvent, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            textx = int((1000-textsize[0])/2)
            ConsoleImg = textOn(ConsoleImg, curEvent, pos = (textx, 18), scale = 0.6, lineWidth = 1, color=(0, 0, 0))
        
        ## page change handle4 ##
        if keyboard.is_pressed("right"):
            ConsoleImg = rightArrow(ConsoleImg, clr=(255, 100, 100))
            ConsoleImg = leftArrow(ConsoleImg)
            if ((time.time()-last_page_change) > page_change_rate) and (isActiveWindow()):
                ActivePage+=1
                last_page_change = time.time()
        elif keyboard.is_pressed("left"):
            ConsoleImg = rightArrow(ConsoleImg)
            ConsoleImg = leftArrow(ConsoleImg, clr=(255, 100, 100))
            if ((time.time()-last_page_change) > page_change_rate) and (isActiveWindow()):
                ActivePage-=1
                last_page_change = time.time()
        else:
            ConsoleImg = rightArrow(ConsoleImg)
            ConsoleImg = leftArrow(ConsoleImg)
                
        ActivePage=ActivePage%page_count
        ## end ## 
        isLoadingConsole = False
        time.sleep(0.05)
        
#shows images that above managers want to be shown & ends program on "X" button
def GUI_RENDERER():
    global ConsoleImg
    global isLoadingConsole
    
    while True:
        while isLoadingConsole and (cv2.getWindowProperty(CONSOLE_WINDOW_NAME, 0)>=0):
            time.sleep(0.0001)
        if cv2.getWindowProperty(CONSOLE_WINDOW_NAME, 0)<0: #if console is closed, end program
            END_ALL_PROC()
            return None
            
        cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
        cv2.waitKey(50)

consoleMan = Thread(target = CONSOLE_MANAGER)
consoleMan.start()
scanHandler = Thread(target = GUI_RENDERER)
scanHandler.start()
eventHandler = Thread(target = EventHandler)
eventHandler.start()

#################
        
## ID SCANNER ##
def scannedID(id):
    global EventQueue
    event = "scanned:" + str(id)
    EventQueue.insert(0, event)
    
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

consoleMan.join()
scanHandler.join()
eventHandler.join()
