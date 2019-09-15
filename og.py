from threading import Thread
import time
import pythoncom, pyHook
import cv2
import numpy as np
import sys
import math
import datetime

login_img = np.zeros((400, 500, 3), np.uint8)
logout_img = np.zeros((400, 500, 3), np.uint8)

def setLoginImg(id):
	global login_img
	cv2.rectangle(login_img, (0,0), (500,400), (150, 255, 150), -1)
	cv2.putText(login_img, "Welcome", (100, 70), cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), lineType=cv2.LINE_AA, thickness = 2) 
	cv2.putText(login_img, str(id), (10, 275), cv2.FONT_HERSHEY_COMPLEX, 4.0, (0, 0, 0), lineType=cv2.LINE_AA, thickness = 5) 
	
	
def setLogoutImg(id):
	global logout_img
	cv2.rectangle(logout_img, (0,0), (500,400), (150, 150, 255), -1)
	cv2.putText(logout_img, "Goodbye", (100, 70), cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), lineType=cv2.LINE_AA, thickness = 2) 
	cv2.putText(logout_img, str(id), (10, 275), cv2.FONT_HERSHEY_COMPLEX, 4.0, (0, 0, 0), lineType=cv2.LINE_AA, thickness = 5) 


curID = ""
lastAdd = time.time()
time_thresh = 1

### CONSOLE BUILDING
conImg = np.zeros((600, 700, 3), np.uint8)

def resetConsole():
	global conImg
	cv2.rectangle(conImg, (0, 0), (700, 600), (25, 25, 25), -1) #background color

	cv2.putText(conImg, "made by gabe", (45, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (235, 235, 235), lineType=cv2.LINE_AA, thickness = 1) 
	cv2.putText(conImg, "v1.4.2", (550, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (235, 235, 235), lineType=cv2.LINE_AA, thickness = 1) 

	cv2.putText(conImg, "Attendance", (155, 50), cv2.FONT_HERSHEY_COMPLEX, 2.0, (235, 235, 235), lineType=cv2.LINE_AA, thickness = 2) 
	cv2.putText(conImg, "Logger", (230, 110), cv2.FONT_HERSHEY_COMPLEX, 2.0, (235, 235, 235), lineType=cv2.LINE_AA, thickness = 2) 

	#column tops
	cv2.line(conImg, (25, 150), (337, 150), (255, 255, 255), 1)
	cv2.line(conImg, (363, 150), (675, 150), (255, 255, 255), 1)

	#column bottoms
	cv2.line(conImg, (25, 575), (337, 575), (255, 255, 255), 1)
	cv2.line(conImg, (363, 575), (675, 575), (255, 255, 255), 1)

	#column sides
	cv2.line(conImg, (25, 150), (25, 575), (255, 255, 255), 1)
	cv2.line(conImg, (337, 150), (337, 575), (255, 255, 255), 1)

	cv2.line(conImg, (363, 150), (363, 575), (255, 255, 255), 1)
	cv2.line(conImg, (675, 150), (675, 575), (255, 255, 255), 1)
	###

	for i in range(1, 18):
		height = 25*i + 150
		cv2.line(conImg, (25, height), (337, height), (255, 255, 255), 1)
		
	for i in range(1, 18):
		height = 25*i + 150
		cv2.line(conImg, (363, height), (675, height), (255, 255, 255), 1)

resetConsole()

cv2.imshow("Console - gabe > everyone", conImg)
### END CONSOLE


CURRENT_LOGGED_IN = []
'''
["yoda", time.time()], 
["is", time.time()], 
["dummy", time.time()],
["thicc", time.time()],
["_1", time.time()],
["_2", time.time()],
["_3", time.time()],
["_4", time.time()],
["_5", time.time()], 
["_6", time.time()]]
'''

DIE_THREAD = False
def tryThread():
	global DIE_THREAD
	global conImg
	while cv2.getWindowProperty('Console - gabe > everyone', 0) >= 0:
		resetConsole()
		#Draw logged in people
		i=1
		for member in CURRENT_LOGGED_IN:
			height = 25*i + 145
			left = 27
			if i>17:
				left = 365
				height-= 25*17
			cv2.putText(conImg, str(member[0]), (left, height), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), lineType=cv2.LINE_AA)
			
			t = math.floor(time.time()-member[1])
			duration = datetime.timedelta(seconds=t)
			duration = str(duration)
			#duration = "hello"
			cv2.putText(conImg, duration, (left + 310 - len(duration)*12, height), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), lineType=cv2.LINE_AA)
			
			
			i+=1
		#
		
		
		cv2.imshow("Console - gabe > everyone", conImg)
		cv2.waitKey(100)
		print("showing img")
	print("thread ded")
	sys.exit()
		


worker = Thread(target = tryThread)
worker.start()
#con = Thread(target=console, args=[])
#con.start()
#print("done")

def asNum(key):
	if key=="0":
		return 'zero' #0==False
	if key=="1":
		return 1
	if key=="2":
		return 2
	if key=="3":
		return 3
	if key=="4":
		return 4
	if key=="5":
		return 5
	if key=="6":
		return 6
	if key=="7":
		return 7
	if key=="8":
		return 8
	if key=="9":
		return 9
	return False

def handleLogin(id):
	global CURRENT_LOGGED_IN
	global conImg
	
	i = 0
	for member in CURRENT_LOGGED_IN:
		if member[0] == id:
			CURRENT_LOGGED_IN.remove(member)
			return False
		i+=1
	CURRENT_LOGGED_IN.append([id, time.time()])
	return True

def OnKeyboardEvent(event):
	global curID
	global lastAdd
	
	doContinue = True
	key = event.Key
	
	if (time.time()-lastAdd)>time_thresh:
		if len(curID)==0:
			lastAdd = time.time()
		else:
			print("u too slow")
			curID = ""
			lastAdd = time.time()
	
	
	if key=="Return" and doContinue:
		if len(curID) == 6:
			print("-----")
			print("Id scanned: " + curID)
			print("-----")
			
			login = handleLogin(curID)
			
			if login:
				setLoginImg(curID)
				cv2.imshow("ATTENDANCE - gabe is cool", login_img)
			else:
				setLogoutImg(curID)
				cv2.imshow("ATTENDANCE - gabe is cool", logout_img)
			
			start = time.time()
			while (time.time()-start)<1:
				cv2.waitKey(1)
			cv2.destroyWindow("ATTENDANCE - gabe is cool")
			curID = ""
			lastAdd = time.time()
			doContinue = False
		else:
			print("FAILED-earlyReturn")
			print("Tried to submit '"+curID+"'")
		curID = ""
		doContinue = False
		
	if(asNum(key)) and doContinue:
		curID+=str(key)
		print("added: "+key)
	elif doContinue:
		print("FAILED-ALPHABETICAL")
		curID = ""
		doContinue = False
	if len(curID) > 6 and doContinue:
		print("FAILED-TOO LONG")
		curID = ""
		doContinue = False
	lastAdd = time.time()
	# return True to pass the event to other handlers
	return True

# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()

print("here")
DIE_THREAD = True
cv2.waitKey(50)
cv2.destroyAllWindows()
