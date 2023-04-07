import pyttsx3
from bs4 import BeautifulSoup

import cv2
import mediapipe as mp
import time
import requests
import datetime
import keyboard

def findPosition(img, handNo = 0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])

    return lmList


engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# -------------------------------------------

cam = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

previousTime = 0
currentTime = 0

fingerIDs = [4, 8, 12, 16, 20]
lock = False
startTime = 0

while True:
    startFreddy = False
    isCameraOn = False

    if keyboard.is_pressed('f9'):
        cam = cv2.VideoCapture(0)
        startFreddy = True
        time.sleep(0.5)

    time.sleep(0.5)

    while startFreddy:
        if keyboard.is_pressed('f9'):
            cam.release()
            cv2.destroyAllWindows()
            time.sleep(1)
            break

        if keyboard.is_pressed('f10'):
            isCameraOn = not isCameraOn
            time.sleep(1)

        success, img = cam.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        lmList = findPosition(img)
        if len(lmList) != 0:
            fingers = []

            # Thumb
            if lmList[fingerIDs[0]][1] > lmList[fingerIDs[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if lmList[fingerIDs[id]][2] < lmList[fingerIDs[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # Lock....
            if fingers == [1, 1, 0, 0, 1] and not lock:
                lock = True
                startTime = time.time()

            # Iot Light....
            if fingers == [0, 1, 1, 0, 0] and lock:
                # requests.get("https://sgp1.blynk.cloud/external/api/update?token=OOKPeVDEs478qZWuyupcuwIBLPnHShno&v4=0")
                requests.get("https://sgp1.blynk.cloud/external/api/update?token=ecZr-286_DVvbwLQSPoYupQ8uUxPzLJd&v1=0")
                speak("Your light is turned on")
                lock = False
            elif fingers == [1, 0, 0, 0, 1] and lock:
                # requests.get("https://sgp1.blynk.cloud/external/api/update?token=OOKPeVDEs478qZWuyupcuwIBLPnHShno&v4=1")
                requests.get("https://sgp1.blynk.cloud/external/api/update?token=ecZr-286_DVvbwLQSPoYupQ8uUxPzLJd&v1=1")
                speak("Your light is turned off")
                lock = False

            elif fingers == [1, 1, 1, 0, 1] and lock:
                requests.get("https://sgp1.blynk.cloud/external/api/update?token=sQtCJITWODERH-vvGtxENNdfWWuhRJk-&v2=1")
                speak("Ahmed's lights are turned off")
                lock = False

            # Temperature....
            elif fingers == [0, 0, 1, 1, 1] and lock:
                search = "temperature in jeddah"
                url = f"https://www.google.com.sa/search?q={search}"
                req = requests.get(url)
                data = BeautifulSoup(req.text, "html.parser")
                temp = data.find("div", class_="BNeawe").text
                speak(f"The current {search} is {temp} celsius")
                lock = False

            # Time....
            elif fingers == [1, 1, 1, 1, 0] and lock:
                strTime = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"Sir, the time is {strTime}")
                lock = False

        if time.time() - startTime > 1 and lock:
            lock = False

        currentTime = time.time()
        fps = 1 / (currentTime - previousTime)
        previousTime = currentTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (42,177,23), 3)

        if isCameraOn:
            cv2.imshow("Freddy", img)
        else:
            cv2.destroyAllWindows()
        cv2.waitKey(1)