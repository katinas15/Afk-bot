import cv2 as cv
import numpy as np
import os
from time import time
import ctypes
import time
import vgamepad as vg
import pyautogui
import random



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

path_to_tesseract = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract








SendInput = ctypes.windll.user32.SendInput

# W = 0x11
# A = 0x1E
# S = 0x1F
# D = 0x20
# E = 0x12
# Z = 0x2C
# UP = 0xC8
# DOWN = 0xD0
# LEFT = 0xCB
# RIGHT = 0xCD
# ENTER = 0x1C 

# Full list - http://web-old.archive.org/web/20190801085838/http://www.gamespp.com/directx/directInputKeyboardScanCodes.html

# TODOThings 1 - Add time randomizattion for keypress events 2 - Only cap middle of screen 200x200 pixels for fastter and more accurate matching 3 - Make code less ghetto kekw 

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def pressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def releaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, 
ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))



# COOLDOWN_ICON_LOCATION = (659, 523)
COOLDOWN_ICON_LOCATION = (653, 522)

COOLDOWN_ICON_DIM = (31,31)
FISHING_MARK_LOCATION = (300, 620)
FISHING_MARK_DIM = (50,30)
# ex_images = [Vision2('ex_mark.png'), Vision2('ex_mark2.png'), Vision2('ex_mark3.png'), Vision2('ex_mark4.png'), Vision2('ex_mark5.png')]
# cooldown_images = [Vision2('fish_cooldown.png'), Vision2('fish_cooldown2.jpg')]
# fish_active = Vision2('fish_cooldown_active.png')
# fish_inactive = Vision2('fish_cooldown_inactive.png')
is_fishing = False
click_delay_after_catch = 6
detection_threshold = 0.6
fish_inactive_delay = 4

import time
time_fish_caught = time.time()
first_time_fishing_inactive = time.time()


def crop_fishing_mark(img):
    y = FISHING_MARK_LOCATION[0]
    x = FISHING_MARK_LOCATION[1] 
    h = FISHING_MARK_DIM[0]
    w = FISHING_MARK_DIM[1]
    crop_img = img[y:y + h, x:x + w]
    return crop_img

def crop_fish_cooldown(img):
    y = COOLDOWN_ICON_LOCATION[0]
    x = COOLDOWN_ICON_LOCATION[1] 
    h = COOLDOWN_ICON_DIM[0]
    w = COOLDOWN_ICON_DIM[1]
    crop_img = img[y:y + h, x:x + w]
    return crop_img






MINIMAP_LOCATION = (1080, 15)
MINIMAP_DIM = (180,160)
MINIMAP_CENTER = (MINIMAP_DIM[0]/2.0, MINIMAP_DIM[1]/2.0)
gamepad = vg.VX360Gamepad()
    
def crop_image(screenshot, location, dimensions):
    x = location[0]
    y = location[1] 
    w = dimensions[0]
    h = dimensions[1]
    return screenshot[y:y + h, x:x + w]

def mask_minimap(image):
    lower = np.array([0,75,150], dtype = "uint8")
    upper = np.array([255,255,255], dtype = "uint8")

    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower, upper)  
    return mask

def get_minimap():
    return crop_image(wincap.get_screenshot(), MINIMAP_LOCATION, MINIMAP_DIM)
    
def find_item_in_image(screenshot, template, threshold = .6):
    w, h = template.shape[:-1]
    res = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    
    loc = np.where(res >= threshold)
    item_location = loc[::-1]

    for pt in zip(*item_location):  # Switch collumns and rows
        cv.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    return (item_location, screenshot)

def gamepad_movement(up, right):
    gamepad.left_joystick_float(x_value_float=right, y_value_float=up)
    gamepad.update()
    time.sleep(random.uniform(0.3, 1.0))
    gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
    gamepad.update()

LOCATION_LOG = []

def move_to_location(location, center):
    MOVEMENT_THRESHOLD = 10

    try: 
        right = center[0] - location[0][0]
        print(right)
        if  right > MOVEMENT_THRESHOLD:
                right = -1.0
        elif  right < MOVEMENT_THRESHOLD:
                right = 1.0
        else:
                right = 0

        up = center[1] - location[1][0]
        print(up)
        if up > MOVEMENT_THRESHOLD:
            up = 1.0
        elif up < MOVEMENT_THRESHOLD:
            up = -1.0
        else:
            up = 0

        if len(LOCATION_LOG) > 3:
            location_sum = [0]
            LOCATION_LOG.pop()
            location_sum = (LOCATION_LOG[0][0] - LOCATION_LOG[1][0] - LOCATION_LOG[2][0]) + \
            (LOCATION_LOG[0][1] - LOCATION_LOG[1][1] - LOCATION_LOG[2][1]) 
            print(location_sum[0])
            if abs(location_sum[0]) < 40:
                print('unstuck')
                gamepad_movement(not up, right)
                gamepad_movement(not up, right)


        print(location)
        LOCATION_LOG.append(location)



        gamepad_movement(up, right)
    except Exception as e:
        print(e)


DESTROYER_SPELLS = [
    {"button": 0x10, "duration": 2, "cooldown": 5 * 2, "last_cast": 0},
    {"button": 0x11, "duration": 3, "cooldown": 10 * 2, "last_cast": 0},
    {"button": 0x12, "duration": 5, "cooldown": 18, "last_cast": 0},
    {"button": 0x13, "duration": 3, "cooldown": 10 * 2, "last_cast": 0},
    {"button": 0x1E, "duration": 2, "cooldown": 30, "last_cast": 0},
    {"button": 0x1F, "duration": 5, "cooldown": 24, "last_cast": 0},
    {"button": 0x20, "duration": 5, "cooldown": 30, "last_cast": 0},
    {"button": 0x21, "duration": 2, "cooldown": 14, "last_cast": 0},
]

GUNLANCER_SPELLS = [
    {"button": 0x10, "duration": 2, "cooldown": 20, "last_cast": 0},
    {"button": 0x11, "duration": 3, "cooldown": 30, "last_cast": 0},
    {"button": 0x12, "duration": 1, "cooldown": 30, "last_cast": 0},
    {"button": 0x13, "duration": 2, "cooldown": 16, "last_cast": 0},
    {"button": 0x1E, "duration": 2, "cooldown": 12, "last_cast": 0},
    {"button": 0x1F, "duration": 2, "cooldown": 9, "last_cast": 0},
    {"button": 0x20, "duration": 2, "cooldown": 18, "last_cast": 0},
    {"button": 0x21, "duration": 2, "cooldown": 5, "last_cast": 0},
]

DEADEYE_SPELLS = [
    {"button": 0x10, "duration": 3, "cooldown": 16, "last_cast": 0},
    {"button": 0x11, "duration": 1, "cooldown": 6, "last_cast": 0},
    {"button": 0x12, "duration": 1, "cooldown": 8, "last_cast": 0},
    {"button": 0x13, "duration": 2, "cooldown": 18, "last_cast": 0},
    {"button": 0x1E, "duration": 1, "cooldown": 8, "last_cast": 0},
    {"button": 0x1F, "duration": 2, "cooldown": 12, "last_cast": 0},
    {"button": 0x20, "duration": 2, "cooldown": 6, "last_cast": 0},
    {"button": 0x21, "duration": 2, "cooldown": 9, "last_cast": 0},
]

def cast_spell(spell_button, duration):
    pressKey(spell_button)
    time.sleep(duration)
    releaseKey(spell_button)


def check_death():
    print("checking if dead")
    screenshot = wincap.get_screenshot()
    found_location, modified_screenshot = find_item_in_image(screenshot, RESPAWN_IMAGE)
    # cv.imshow('UI', modified_screenshot)   

    if len(found_location[0]) == 0:
        return
    else:
        print('clicking respawn')
        pyautogui.moveTo(900, 330)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)


def check_dungeon_time_ended():
    print("checking if dungeon time ended")
    screenshot = wincap.get_screenshot()
    found_location, modified_screenshot = find_item_in_image(screenshot, TIME_ZERO_IMAGE, 0.8)
    # cv.imshow('UI', modified_screenshot)   

    if len(found_location[0]) == 0:
        return False
    else:
        print('dungeon time ended')
        pyautogui.moveTo(115, 200)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)


        print('leaving dungeon')
        pyautogui.moveTo(610, 430)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)
        return True


def check_dungeon_victory():
    print("checking if dungeon victory")
    screenshot = wincap.get_screenshot()
    found_location, modified_screenshot = find_item_in_image(screenshot, VICTORY_IMAGE, 0.8)
    # cv.imshow('UI', modified_screenshot)   

    if len(found_location[0]) == 0:
        return False
    else:
        print('VICTORY')
        pyautogui.moveTo(650, 670)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)

        pyautogui.moveTo(115, 200)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)


        print('leaving dungeon')
        pyautogui.moveTo(610, 430)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(20)
        return True


def combat(spells):
    check_death()
    if check_dungeon_time_ended():
        return

    if check_dungeon_victory():
        return
    print('attacking')

    gamepad_movement(random.choice([True, False]), random.choice([True, False]))
    
    for spell in spells:
        print(spell)
        if time.time() - spell["last_cast"] > spell["cooldown"] or not spell["last_cast"]:
            cast_spell(spell["button"], spell["duration"])
            spell["last_cast"] = time.time()
            return


ITEM_LOCATION_LOG = []


    



    

















def open_dungeons_ui():
    print("opening dengeons ui")

    for i in range(5):
        print("opening dengeons ui again")
        screenshot = wincap.get_screenshot()
        found_location, modified_screenshot = find_item_in_image(screenshot, CHAOS_DUNGEON_IMAGE)
        # cv.imshow('UI', modified_screenshot)   

        print(found_location)

        if len(found_location[0]) == 0:
            with pyautogui.hold('altleft'):
                pyautogui.press(['q'])

            time.sleep(2)
        else:
            return


def open_chaos_dungeon_ui():
    print('clicking on chaos dungeons')
    pyautogui.moveTo(577, 225)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(3)

def queue_dungeon():
    print("queueing for dungeon")
    pyautogui.moveTo(1025, 600)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(3)

def confirm_dungeon():
    print("confirm for dungeon")
    pyautogui.moveTo(600, 420)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(3)

def is_in_dungeon():
    print("checking if already in dungeon")
    screenshot = wincap.get_screenshot()
    found_location, modified_screenshot = find_item_in_image(screenshot, IN_DUNGEON_IMAGE)
    # cv.imshow('UI', modified_screenshot)   

    print(found_location)

    if len(found_location[0]) == 0:
        return False
    else:
        return True

def get_into_chaos_dungeon():
    print("trying to get into dungeons")
    if is_in_dungeon():
        return

    open_dungeons_ui()

    if is_in_dungeon():
        return

    open_chaos_dungeon_ui()

    if is_in_dungeon():
        return

    queue_dungeon()

    if is_in_dungeon():
        return

    confirm_dungeon()

    if is_in_dungeon():
        return

    time.sleep(10)




def open_pet_functions(location):
    print("opening pet functions")
    w, h = PET_IMAGE.shape[:-1]
    with pyautogui.hold('ctrl'):
        pyautogui.moveTo(location[0] + w, location[1] + h)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(3)

            # print("repairing items")
    # location_images = [
    #     {"image": PET_IMAGE, "amount": 1},
    #     {"image": PET2_IMAGE, "amount": 1},
    # ]
    # minimap_screenshot = wincap.get_screenshot()
    # move_location = ([], [])

    # for location_image in location_images:
    #     location, minimap_screenshot = find_item_in_image(minimap_screenshot, location_image["image"])
    #     cv.imshow('detection', minimap_screenshot) 
    #     # print(location_image)
    #     if len(location[0]) >= location_image["amount"]:
    #         move_location = location

    # print(len(move_location[0]))
    # if len(move_location[0]) != 0:
    #     open_pet_functions(move_location)
    # else:
    #     pass

def get_tesserract_text(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    img = ImageGrab.grab(bbox=(top_left_x, top_left_y, bottom_right_x, bottom_right_y))
    img = np.array(img)
    resized = cv2.resize(img,(0,0),fx=3, fy=3)
    text = pytesseract.image_to_string(resized)
    return resized, text



def check_afk():
    print("tikrina afk")
    top_left_x = 1095
    top_left_y = 500
    bottom_right_x = 1145
    bottom_right_y = 530
    
    resized, text = get_tesserract_text(top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    
    print(text[:-1])
    print(len(text))
    if len(text) == 5:
        print(text[:-1])
        time.sleep(AFK_INPUT_DELAY)
        pyautogui.write(text)
        keyboard.press(Key.enter)
        sleep(1)
        keyboard.release(Key.enter) 

    resized = cv2.resize(resized, (960, 540)) 
    frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    cv2.imshow("afk", frame)
        

def check_fishing_spots():
    print("tikrina fishing")
    top_left_x = 300
    top_left_y = 400
    bottom_right_x = 1280
    bottom_right_y = 720
    
    resized, text = get_tesserract_text(top_left_x, top_left_y, bottom_right_x, bottom_right_y)

    print(text[:-1])
    print(len(text))
    if len(text) == 6:
        print(text[:-1])
        pyautogui.write(text)
        keyboard.press(Key.enter)
        sleep(1)
        keyboard.release(Key.enter) 

    resized = cv2.resize(resized, (960, 540)) 
    frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    cv2.imshow("fishing", frame)


SPAM_BUTTONS = [0x12]
def spam_e():
    print('pressing E')
    for button in SPAM_BUTTONS:
        pressKey(button)
        time.sleep(0.1)
        releaseKey(button)

def fishing():
    print('fishing')
    spam_e()

print("booting up")
time.sleep(5)

FRAME_UPDATE = 0.1
AFK_INPUT_DELAY = 5
last_frame_update = time.time()
while(True):
    t = time.time()
    if(t - last_frame_update > FRAME_UPDATE):
        print(t - last_frame_update)
        check_afk()
        last_frame_update = time.time()



    # fishing()

    # print('show')
    # frame = cv2.cvtColor(get_minimap(), cv2.COLOR_BGR2RGB)
    # frame = np.array(frame, dtype = np.uint8 )
    # cv2.imshow("frame", frame)
    if cv.waitKey(20) == ord('q'):
        cv.destroyAllWindows()
        break


print('Done.')
