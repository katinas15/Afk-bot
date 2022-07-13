from pynput.keyboard import Controller
from pynput.keyboard import Key
from pytesseract import pytesseract
import cv2
from pynput.mouse import  Controller as Ctrll_2
from pynput.mouse import  Button
from time import sleep
import numpy as np
import pyautogui
from PIL import ImageGrab

keyboard = Controller()
mouse = Ctrll_2()

path_to_tesseract = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract





while True:
    print("tikrina")
    #Grabina nuotrauka is nustatytu kordinaciu
    img = ImageGrab.grab(bbox=(1095, 475, 1145, 515))
    #Pavercia i numpy masyva
    img = np.array(img)
    #pakeicia dimensijas siekiant gauti kokybeskesni vaizda
    resized = cv2.resize(img,(0,0),fx=3, fy=3)
    #P Is nuotraukos transformuoja i kintamaji
    text = pytesseract.image_to_string(resized)
    
    print(text[:-1])
    print(len(text))
    if len(text) == 6:
        print(text[:-1])
        pyautogui.write(text)
        keyboard.press(Key.enter)
        sleep(1)
        keyboard.release(Key.enter) 
    frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0Xff == ord('q'):
        break

    