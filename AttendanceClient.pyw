ALLOWED_TIME_BETWEEN_KEY_PRESSES = 0.1 #lower = faster key presses required
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
import urllib.request, json 
import random

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
    
def asHHMMSS(sec):
    hh = str(math.floor( sec/(60*60)      ))
    mm = str(math.floor( (sec/60)%60      ))
    ss = str(math.floor( (sec)%60         ))
    if len(hh)==1:
        hh = "0"+hh
    if len(mm)==1:
        mm = "0"+mm
    if len(ss)==1:
        ss = "0"+ss
    st = hh+":"+mm+":"+ss
    return st
    
def asSeconds(HHMMSS):
    hh, mm, ss = HHMMSS.split(":")
    return (int(hh)*60*60 + int(mm)*60 + int(ss))
    
def getjson(url):
    try:
        with urllib.request.urlopen(url) as response:
            val = json.loads(response.read().decode())
            return (True, val)
    except Exception as e: 
        print(e)
        return (False, "ERROR: 404")
    
def api_reach(directory):
    success, JSON = getjson("http://3863.us/" + directory)
    if success:
        if JSON["error"] != 0:
            return (False, JSON["error"])
    return (success, JSON)
    
def drawRoundedRectangle(img, begin, end, color, radius = 10):
    cv2.rectangle(img, (begin[0], begin[1]+radius), (end[0], end[1]-radius), color, -1)
    cv2.rectangle(img, (begin[0]+radius, begin[1]), (end[0]-radius, end[1]), color, -1)
    cv2.circle(img, (begin[0]+radius, begin[1]+radius), radius, color, -1)
    cv2.circle(img, (end[0]-radius, end[1]-radius), radius, color, -1)
    cv2.circle(img, (begin[0]+radius, end[1]-radius), radius, color, -1)
    cv2.circle(img, (end[0]-radius, begin[1]+radius), radius, color, -1)
    return img
    
def DrawRoundedOutlinedRectangle(img, begin, end, innercolor, bordercolor, radius = 10, border = 5):
    if (end[0]-begin[0]) < radius*2:
        radius = int(math.floor((end[0]-begin[0])/2))
    if (end[1]-begin[1]) < radius*2:
        radius = int(math.floor((end[1]-begin[1])/2))
    drawRoundedRectangle(img, (begin[0]-border, begin[1]-border), (end[0]+border, end[1]+border), bordercolor, radius = radius)
    drawRoundedRectangle(img, begin, end, innercolor, radius = radius)
    return img
        
####################

## GUI MANAGER ##
CurrentPresence = {"updated" : 0, "info" : []}
EventQueue = []
curEvent = ""

LastLogout = 0
LastErrorScan = 0
LastLogin = 0
LastLoginOutPerson = ""

def EventHandler():
    global EventQueue
    global curEvent
    global CurrentPresence
    global LastLogout
    global LastErrorScan
    global LastLogin
    global LastLoginOutPerson
    while True:
        while len(EventQueue)==0:
            time.sleep(0.01)
        cmd = EventQueue[0]
        curEvent = cmd
        cmdTyp, cmdVal = cmd.split(":")
        curEvent = cmdTyp
        if cmdTyp == "UPDATE":
            if cmdVal == "presence":
                curEvent = "accessing api for presence update"
                start = time.time()
                succ, val = api_reach("GetCurrentPresence.php?psswd=nphs3863")
                while time.time()-start < 0.1: #waitAsync
                    time.sleep(0.01)
                if succ:
                    if val["error"] == 0:
                        curEvent = "retrieved presence info"
                        start = time.time()
                        tempPresence = {"updated" : start, "info" : []}
                        for id_s in val['result']:
                            _, id = id_s.split("-")
                            info = val['result'][id_s]
                            name = info['name']
                            elapsed = info['elapsedTime']
                            elapSeconds = asSeconds(elapsed)
                            tempPresence["info"].append({"id" : id,"name" : name, "elapsedTime" : elapSeconds})
                        CurrentPresence = tempPresence
                        while time.time()-start < 0.1:  #waitAsync
                            time.sleep(0.01)
                        EventQueue.remove(cmd)
                    else:
                        curEvent = "ERR: " + str(val["error"])
                        time.sleep(0.1)
                else:
                    curEvent = "ERR: API-NO-RESPONSE"
                    time.sleep(0.1)
            else:
                curEvent = "unknown command: " + cmd
                time.sleep(0.1)
                EventQueue.remove(cmd)
        elif cmdTyp == "scanned":
            curEvent = "ID input: " + cmdVal
            start = time.time()
            succ, val = api_reach("ScannedId.php?psswd=nphs3863&id=" + cmdVal)
            if succ:
                if val["isPresent"]:
                    curEvent = "logging in..."
                    CurrentPresence["info"].append({"id" : val["id"] ,"name" : val["Name"], "elapsedTime" : int(time.time()-start)})
                    LastLogin = time.time()
                    LastLoginOutPerson = val["id"] if val["Name"] == "Unknown" else val["Name"]
                    time.sleep(0.1)
                else:
                    curEvent = "logging out..."
                    for member in CurrentPresence["info"]:
                        if member["id"] == val["id"]:
                            CurrentPresence["info"].remove(member)
                            LastLogout = time.time()
                            LastLoginOutPerson = val["id"] if val["Name"] == "Unknown" else val["Name"]
                    time.sleep(0.1)
            else:
                curEvent = "ERR: API-NO-RESPONSE"
                LastErrorScan = time.time()
                time.sleep(0.1)
            while time.time()-start < 0.1: #waitAsync
                time.sleep(0.01)
            EventQueue.remove(cmd)
        elif cmdTyp == "terminateAll":
            curEvent = "Terminating All Sessions"
            start = time.time()
            succ, val = api_reach("SignAllOut.php?psswd=nphs3863")
            if succ:
                if val["error"] == 0:
                    curEvent = "Accounts affected: " + str(val["affectedPeopleCount"])
                    CurrentPresence = {"updated" : time.time(), "info" : []}
                    time.sleep(3)
                    while time.time()-start < 0.1:  #waitAsync
                        time.sleep(0.01)
                    EventQueue.remove(cmd)
                else:
                    curEvent = "ERR: " + str(val["error"])
                    time.sleep(0.1)
            else:
                curEvent = "ERR: API-NO-RESPONSE"
                time.sleep(0.1)
        elif cmdTyp == "Clear" and cmdVal == "myself":
            curEvent = "Clearing queue"
            EventQueue = []
            time.sleep(0.1)
        else:
            curEvent = "unknown command: " + cmd
            time.sleep(3)
            EventQueue.remove(cmd)
        curEvent = ""
        
def PresenceUpdater():
    global EventQueue
    minutes_between_updates = 5 #update every 5 minutes
    while True:
        EventQueue.append("UPDATE:presence")
        time.sleep((minutes_between_updates)*60)

confirmationPrompt = False
confirmationQuestion = ""
confirmationResult = False
confirmationTimeBegan = 0
def areYouSure(question):
    global confirmationPrompt
    global confirmationResult
    global confirmationQuestion
    global confirmationTimeBegan
    confirmationQuestion = question
    confirmationPrompt = True
    confirmationTimeBegan = time.time()
    while confirmationPrompt==True:
        time.sleep(0.01)
    toreturn = confirmationResult
    #cleanup
    confirmationPrompt = False
    confirmationQuestion = ""
    confirmationResult = False
    #sendresult
    return toreturn
    
#decides what mage is to be shown in console
ConsoleImg = blackImg(1000, 600)
cv2.imshow(CONSOLE_WINDOW_NAME, ConsoleImg)
lastConIsActive = True
conActiveSwitchedAt = time.time()
ActivePage = 0
page_count = 4 #+1 for debug
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
    global CurrentPresence
    global LastLogout
    global LastErrorScan
    global LastLogin
    global LastLoginOutPerson
    global confirmationPrompt
    global confirmationResult
    global confirmationQuestion
    global confirmationTimeBegan
    hproc_start_time = time.time()
    while True:
        hproc_elapsed_time = time.time()-hproc_start_time
        isLoadingConsole = True #prevent GUI_RENDERER from loading imcomplete image
        ConsoleImg = 17 * np.ones((600,1000,3), np.uint8) # reset to dark gray background
        
        if ActivePage == 0:
            
            textsize = cv2.getTextSize("Attendance Recorder", cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
            ConsoleImg = textOn(ConsoleImg, "Attendance Recorder", pos = (500 - int(textsize[0]/2), textsize[1] + 30), scale = 2, lineWidth = 4, color=(255, 255, 255))
            
            ConsoleImg = cv2.rectangle(ConsoleImg, (100, 100), (475, 550), (255,255,255), 2)
            ConsoleImg = cv2.rectangle(ConsoleImg, (525, 100), (900, 550), (255,255,255), 2)
            
            for i in range(1, 18):
                h = i*25 + 100
                ConsoleImg = cv2.line(ConsoleImg, (100, h), (475, h), (255,255,255), 1)
                ConsoleImg = cv2.line(ConsoleImg, (525, h), (900, h), (255,255,255), 1)
            
            rowCount = 18
            c = 0
            for member in CurrentPresence["info"]:
                c+=1
                id = member["id"]
                name = member["name"]
                elap = member["elapsedTime"] + int(time.time() - CurrentPresence["updated"])
                dispElap = asHHMMSS(elap)
                dispElapSize = cv2.getTextSize(dispElap, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)[0]
                dispName = id if name == "Unknown" else name
                h = c*25 + 96 if c <= rowCount else (c-rowCount)*25 + 96
                x = 105 if c <= rowCount else 530
                ConsoleImg = textOn(ConsoleImg, dispName, pos=(x, h), scale = 0.75)
                ConsoleImg = textOn(ConsoleImg, dispElap, pos=((x+375)-(dispElapSize[0]+10), h), scale = 0.75)
                
                
        elif ActivePage == 1:
            cew = 100
            buttonrow1_begin = int(   cew            )
            buttonrow1_end = int(     500-(cew/2)    )
            buttonrow2_begin = int(   500+(cew/2)    )
            buttonrow2_end = int(     1000-cew       )
            #Terminate sessions
            innercolor = (150, 100, 75) if keyboard.is_pressed("t") and isActiveWindow() else (250, 200, 150)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin, 75), (buttonrow1_end, 150), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin+7, 75+7), (buttonrow1_begin+68, 75+68), innercolor, (255,255,255), radius = 10, border = 4)
            ConsoleImg = textOn(ConsoleImg, "T", pos=(buttonrow1_begin + 24, 75 + 55), scale = 1.5, lineWidth = 2)
            ConsoleImg = textOn(ConsoleImg, "Terminate", pos=(buttonrow1_begin + 80, 75+35), scale = 0.7, lineWidth = 1)
            ConsoleImg = textOn(ConsoleImg, "ALL sessions", pos=(buttonrow1_begin + 80, 75+55), scale = 0.7, lineWidth = 1)
            #Update Current Presence
            innercolor = (150, 100, 75) if keyboard.is_pressed("u") and isActiveWindow() else (250, 200, 150)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin, 200), (buttonrow1_end, 275), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin+7, 200+7), (buttonrow1_begin+68, 200+68), innercolor, (255,255,255), radius = 10, border = 4)
            ConsoleImg = textOn(ConsoleImg, "U", pos=(buttonrow1_begin + 20, 200 + 55), scale = 1.5, lineWidth = 2)
            ConsoleImg = textOn(ConsoleImg, "Update session list now", pos=(buttonrow1_begin + 76, 200+44), scale = 0.7, lineWidth = 1)
            #button
            innercolor = (150, 100, 75) if keyboard.is_pressed("c") and isActiveWindow() else (250, 200, 150)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin, 325), (buttonrow1_end, 400), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin+7, 325+7), (buttonrow1_begin+68, 325+68), innercolor, (255,255,255), radius = 10, border = 4)
            ConsoleImg = textOn(ConsoleImg, "C", pos=(buttonrow1_begin + 21, 325 + 54), scale = 1.5, lineWidth = 2)
            ConsoleImg = textOn(ConsoleImg, "Clear event queue", pos=(buttonrow1_begin + 80, 325+44), scale = 0.7, lineWidth = 1)
            #button
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow1_begin, 450), (buttonrow1_end, 525), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            
            #button
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow2_begin, 75), (buttonrow2_end, 150), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            #button
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow2_begin, 200), (buttonrow2_end, 275), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            #button
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow2_begin, 325), (buttonrow2_end, 400), (200, 150, 100), (255,255,255), radius = 10, border = 4)
            #button
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (buttonrow2_begin, 450), (buttonrow2_end, 525), (200, 150, 100), (255,255,255), radius = 10, border = 4)
        elif ActivePage == 2:
            ConsoleImg = textOn(ConsoleImg, "page 3: maybe club stats?")
        elif ActivePage == 3:
            ConsoleImg = textOn(ConsoleImg, "Credits", pos = (125, 50))
            credits = ["Director", "Writers","Producer","Executive Producer","Lead Cast","Supporting Cast", "Makeup artist", "Hair stylist", "Director of Photography","Production Designer","Editor","Associate Producer","Costume Designer","Music Composer","Casting Director","Lead Visual Effects Editor", "Extra", "Lighting", "Coloring"]
            i=1
            for credit in credits:
                h = i*26 + 60
                ConsoleImg = textOn(ConsoleImg, "-" + credit, pos = (150, h), scale=0.75)
                ConsoleImg = textOn(ConsoleImg, "Gabe Millikan", pos = (700, h), scale=0.75)
                i+=1
        else: #default
            ConsoleImg = textOn(ConsoleImg, "you shouldn't be seeing this")
            ConsoleImg = textOn(ConsoleImg, EventQueue, pos=(0, 250))
            ConsoleImg = textOn(ConsoleImg, "active: " + str(isActiveWindow()), pos=(0, 300))
            ConsoleImg = textOn(ConsoleImg, "mouse : " + str(mouse1down()), pos=(0, 350))
            ConsoleImg = textOn(ConsoleImg, "page  : " + str(ActivePage), pos=(0, 400))
            
        
        ## draw certanity prompy ##
        if confirmationPrompt:
            elap = time.time()-confirmationTimeBegan
            if elap > 10:
                confirmationResult = False
                confirmationPrompt = False
                elap = 10
            if keyboard.is_pressed("N") and isActiveWindow():
                confirmationResult = False
                confirmationPrompt = False
            elif keyboard.is_pressed("Y") and isActiveWindow():
                confirmationResult = True
                confirmationPrompt = False
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (100, 75), (900, 525), (150, 150, 200), (255,255,255), radius = 10, border = 4)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (125, 435), (475, 500), (150, 225, 150), (255,255,255), radius = 999, border = 3)
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (525, 435), (875, 500), (100, 100, 225), (255,255,255), radius = 999, border = 3)
            textsize = cv2.getTextSize("Are you sure that you would like to:", cv2.FONT_HERSHEY_SIMPLEX, 1.25, 2)[0]
            ConsoleImg = textOn(ConsoleImg, "Are you sure that you would like to:", pos=(int(500-(textsize[0]/2)), 150), scale = 1.25, lineWidth = 2)
            textsize = cv2.getTextSize(confirmationQuestion, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            ConsoleImg = textOn(ConsoleImg, confirmationQuestion, pos=(int(500-(textsize[0]/2)), 300), scale = 1.5, lineWidth = 3)
            
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (125+5, 435+5), (125 + 60, 500-5), (150, 225, 150), (255,255,255), radius = 999, border = 2)
            ConsoleImg = textOn(ConsoleImg, "Y", pos=(125+18, 435+50), scale = 1.5, lineWidth = 2)
            ConsoleImg = textOn(ConsoleImg, "Yes", pos=(125+75, 435+50), scale = 1.5, lineWidth = 2)
            
            ConsoleImg = DrawRoundedOutlinedRectangle(ConsoleImg, (525+5, 435+5), (525 + 60, 500-5), (100, 100, 225), (255,255,255), radius = 999, border = 2)
            ConsoleImg = textOn(ConsoleImg, "N", pos=(525+15, 435+48), scale = 1.5, lineWidth = 2)
            ConsoleImg = textOn(ConsoleImg, "No", pos=(525+75, 435+48), scale = 1.5, lineWidth = 2)
            
            ConsoleImg = cv2.rectangle(ConsoleImg, (125, 365), (int((900-125)*(1-(elap/10)) + 125), 370), (255,255,255), -1)
            
            
            
        ##isActiveWindow##
        if lastConIsActive!=isActiveWindow():
            conActiveSwitchedAt = time.time()
            lastConIsActive = not lastConIsActive
        if not lastConIsActive:
            confirmationResult = False
            confirmationPrompt = False
            a = (time.time() - conActiveSwitchedAt)*2
            if a>0.5:
                a=0.5
            ConsoleImg = brighten(ConsoleImg, a)
        else:
            a = (time.time() - conActiveSwitchedAt)*2
            if a<0.5:
                ConsoleImg = brighten(ConsoleImg, 0.5-a)
            
            
            
        ## draw notifier ##
        notifier_show_time = 3 #seconds that the notifier pop-up is shown
        E_e = time.time()-LastErrorScan
        I_e = time.time()-LastLogin
        O_e = time.time()-LastLogout
        if E_e <= I_e and E_e <= O_e and E_e < notifier_show_time:
            ConsoleImg = cv2.rectangle(ConsoleImg, (250, 150), (750, 450), (0, 0, 255), -1)
            textsize = cv2.getTextSize("ERROR", cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)[0]
            textsize = cv2.getTextSize("ERROR", cv2.FONT_HERSHEY_SIMPLEX, 4, 4)[0]
            ConsoleImg = textOn(ConsoleImg, "ERROR", pos=(int(500-(textsize[0]/2)), 300), scale = 4, lineWidth = 4)
            textsize = cv2.getTextSize("(try again)", cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            ConsoleImg = textOn(ConsoleImg, "(try again)", pos=(int(500-(textsize[0]/2)), 375), scale = 1.5, lineWidth = 2)
        elif I_e <= E_e and I_e <= O_e and I_e < notifier_show_time and not confirmationPrompt:
            ConsoleImg = cv2.rectangle(ConsoleImg, (250, 150), (750, 450), (150, 200, 150), -1)
            textsize = cv2.getTextSize("Welcome", cv2.FONT_HERSHEY_SIMPLEX, 3, 4)[0]
            ConsoleImg = textOn(ConsoleImg, "Welcome", pos=(int(500-(textsize[0]/2)), 300), scale = 3, lineWidth = 4)
            textsize = cv2.getTextSize(LastLoginOutPerson, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            ConsoleImg = textOn(ConsoleImg, LastLoginOutPerson, pos=(int(500-(textsize[0]/2)), 375), scale = 1.5, lineWidth = 2)
        elif O_e <= E_e and O_e <= I_e and O_e < notifier_show_time and not confirmationPrompt:
            ConsoleImg = cv2.rectangle(ConsoleImg, (250, 150), (750, 450), (150, 150, 200), -1)
            textsize = cv2.getTextSize("Goodbye", cv2.FONT_HERSHEY_SIMPLEX, 3, 4)[0]
            ConsoleImg = textOn(ConsoleImg, "Goodbye", pos=(int(500-(textsize[0]/2)), 300), scale = 3, lineWidth = 4)
            textsize = cv2.getTextSize(LastLoginOutPerson, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            ConsoleImg = textOn(ConsoleImg, LastLoginOutPerson, pos=(int(500-(textsize[0]/2)), 375), scale = 1.5, lineWidth = 2)
            
            
        ## draw bottom info bar ##
        myIdbuffer = idBuffer
        while len(myIdbuffer) < 6:
            myIdbuffer+="_"
        myIdbuffer+="-"
        if (time.time()-lastAdd) > ALLOWED_TIME_BETWEEN_KEY_PRESSES:
            myIdbuffer = "______-"
        cv2.rectangle(ConsoleImg, (0, 575), (1000, 600), (87, 166, 212), -1)
        ConsoleImg = textOn(ConsoleImg, "time since open: " + asDDHHMMSS(hproc_elapsed_time), pos = (615, 595), scale = 0.75, lineWidth = 2)
        ConsoleImg = textOn(ConsoleImg, "input: " + myIdbuffer, pos = (3, 595), scale = 0.75, lineWidth = 2)
        
        ##draw top info bar ##
        if curEvent!="":
            cv2.rectangle(ConsoleImg, (0, 0), (1000, 20), (230, 230, 230), -1)
            textsize = cv2.getTextSize(curEvent.upper(), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            textx = int((1000-textsize[0])/2)
            ConsoleImg = textOn(ConsoleImg, curEvent.upper(), pos = (textx, 18), scale = 0.6, lineWidth = 1, color=(0, 0, 0))
        
        ## page change handle4 ##
        if keyboard.is_pressed("right"):
            ConsoleImg = rightArrow(ConsoleImg, clr=(255, 100, 100))
            ConsoleImg = leftArrow(ConsoleImg)
            if ((time.time()-last_page_change) > page_change_rate) and (isActiveWindow()):
                ActivePage+=1
                last_page_change = time.time()
                confirmationResult = False
                confirmationPrompt = False
        elif keyboard.is_pressed("left"):
            ConsoleImg = rightArrow(ConsoleImg)
            ConsoleImg = leftArrow(ConsoleImg, clr=(255, 100, 100))
            if ((time.time()-last_page_change) > page_change_rate) and (isActiveWindow()):
                ActivePage-=1
                last_page_change = time.time()
                confirmationResult = False
                confirmationPrompt = False
        else:
            ConsoleImg = rightArrow(ConsoleImg)
            ConsoleImg = leftArrow(ConsoleImg)
                
        ActivePage=ActivePage%page_count
        ## end ## 
        isLoadingConsole = False
        time.sleep(0.05)
        
def ButtonPressHandler():
    global ActivePage
    global EventQueue
    while True:
        if ActivePage == 1 and isActiveWindow():
            if keyboard.is_pressed("t"):
                if areYouSure("Terminate ALL Sessions"):
                    EventQueue.insert(0, "terminateAll:1")
            if keyboard.is_pressed("u"):
                EventQueue.append("UPDATE:presence")
                while keyboard.is_pressed("u"):
                    time.sleep(0.1)
            if keyboard.is_pressed("c"):
                EventQueue.insert(0, "Clear:myself")
                while keyboard.is_pressed("c"):
                    time.sleep(0.1)
        time.sleep(0.01)
        
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
presenceUpdates = Thread(target = PresenceUpdater)
presenceUpdates.start()
buttonMan = Thread(target = ButtonPressHandler)
buttonMan.start()

#################
        
## ID SCANNER ##
def scannedID(id):
    global EventQueue
    event = "scanned:" + str(id)
    EventQueue.insert(0, event) ## put this at the beginning of the queue, cut the line
    
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
