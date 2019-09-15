import pythoncom, pyHook
# download pyhook at https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook
# module pyHook-1.5.1-cp37-cp37m-win32.whl
import time
import cv2
import numpy as np
from threading import Thread

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
    
notifyImg = blackImg(400, 300)
def testThread():
    global notifyImg
    while True:
        print("THREAD WORK")
        cv2.imshow("test", notifyImg)
        cv2.waitKey(10)

thread1 = Thread(target = testThread)
thread1.start()

def keyPressed(event):
    global idBuffer
    global lastAdd
    key = event.Key
    print("processing: " + key)
    # return True to pass the event to other handlers
    return True

hm = pyHook.HookManager()
hm.KeyDown = keyPressed
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()