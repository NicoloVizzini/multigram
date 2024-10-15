
import sys
import os
import time
import shlex
from dataclasses import dataclass
from pathlib import Path
from docopt import docopt
from wmctrl import Window
import cv2
import pyautogui
from .screen_record import capture_screen
import random
import numpy as np
import subprocess
from .utils import *


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int
    def as_tuple(self):
        return (self.x, self.y, self.w, self.h)

TELEGRAM = '/opt/Telegram/Telegram'
ROOT = Path(__file__).parent.parent
ACCOUNTS = ROOT.joinpath('accounts')
ACCOUNTS.mkdir(exist_ok=True)

TELEGRAM_RECT = Rect(x=0, y=0, w=9000, h=900)
#MINIAPP_RECT = Rect(x=259, y=104, w=398, h=705)
MINIAPP_RECT = Rect(x=257, y=158, w=378, h=596)
pyautogui. FAILSAFE = False


def detect_flowers(image, threshold):
    TEMPLATE = cv2.imread("img/flower2.png")
    (tH, tW) = TEMPLATE.shape[:2]
    # convert both the image and template to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(TEMPLATE, cv2.COLOR_BGR2GRAY)
    # perform template matching
    #print("[INFO] performing template matching...")
    result = cv2.matchTemplate(imageGray, templateGray,
        cv2.TM_CCOEFF_NORMED)

    # find all locations in the result map where the matched value is
    # greater than the threshold, then clone our original image so we
    # can draw on it
    (yCoords, xCoords) = np.where(result >= threshold)

    # initialize our list of rectangles
    rects = []
    # loop over the starting (x, y)-coordinates again
    for (x, y) in zip(xCoords, yCoords):
        # update our list of rectangles
        rects.append((x, y, x + tW, y + tH))
    # apply non-maxima suppression to the rectangles
    pick = non_max_suppression(np.array(rects))
    return pick

def non_max_suppression(boxes, overlapThresh=0.3):
    TEMPLATE = cv2.imread("img/flower2.png")
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    # initialize the list of picked indexes
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))
    # return only the bounding boxes that were picked
    return boxes[pick]



def detect_button(image, threshold=0.8):
    # Load the template directly
    TEMPLATE = cv2.imread('img/a.png', 0)
    if TEMPLATE is None:
        raise Exception("Template image not found or could not be loaded.")
    
    w, h = TEMPLATE.shape[::-1]

    # Load the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Match template
    res = cv2.matchTemplate(gray, TEMPLATE, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    # Create a list to hold coordinates
    coordinates = []
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        x_start, y_start = pt
        x_end = x_start + w
        y_end = y_start + h
        coordinates.append((x_start, y_start, x_end, y_end))  # (x_start, y_start, x_end, y_end)

        # Draw a rectangle on the original image for visualization
        cv2.rectangle(image, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)


    return coordinates



def start_blum():
    wait_and_click('img/blum-icon.png',timeout = 7)
    wait_and_click('img/blum-launchx.png', timeout=10)
    try:
        time.sleep(0.51)
        wait_and_click('img/OK.png',timeout =5)
    except Exception as e:
        pass


def cmd_check(options) :
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
    start_blum()
    wait_and_click('img/blum-continue.png',timeout=15)
    time.sleep(1)
    quit(options)

def cmd_check_all(options):
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 3 and not success: #farm isn't that relevant be fast
            try:
                time.sleep(2)
                cmd_check(options)
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1 
                exit_blum()
                exit_telegram()
                if attempts>0:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_check...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")


def cmd_farm(options):
    
    cmd_start(options)
    start_blum()
    
    try:
        wait_and_click('img/blum-farm2.png', timeout=10)
    except Exception as e:
        pass
    try:
        wait_and_click('img/startfarmtribe.png',timeout=10)
    except Exception as e:
        wait_and_click('img/startfarm.png',timeout=10)
    time.sleep(2)
    quit(options)
           

def cmd_farm_all(options):
    log_file_name = "blumr.txt"
    account_name = "placeholder"
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 3 and not success:
            try:
                time.sleep(2)
                cmd_farm(options)
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1
                exit_blum()
                exit_telegram()
                if attempts>0:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_farm...")

        if not success:
            log_failure(i, account_name, log_file_name)
            print(f"Failed to process element {i} after 3 attempts.")
   

    
def exit_blum():
    pyautogui.hotkey('alt', 'f4')

def exit_telegram():
    pyautogui.hotkey('alt', 'f4')


def cmd_blum(options):
    runs = 3
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
    
    def on_threshold_change(value):
        nonlocal THRESHOLD
        THRESHOLD = value / 100

    do_click = not options['--dont-click']
    RECORD = options['--record'] is not None
    if RECORD:
        video_file = options['--record']
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_file, fourcc, 20.0, (RECT.w, RECT.h))
    else:
        out = None

    waitkey_delay = 1
    if options['--video']:
        frames = read_video("screencast.mp4", infinite=True)
        do_click = False
        if options['--step']:
            waitkey_delay = 0
    else:
        start_blum()
        time.sleep(1)
        wait_for_scroll ('img/waitforblum.png',MINIAPP_RECT)
        wait_and_click('img/blum-play2.png',timeout = 10)
        frames = capture_screen(RECT, show_fps=True)

    if SHOW:
        cv2.namedWindow("multigram")
        cv2.createTrackbar("Threshold", "multigram", int(THRESHOLD * 100), 100, on_threshold_change)

    #for i in range(runs):
      #  print("doing run n:")
       # print(i)
        #t = time.time()
    bottone = 0
    t = time.time()
    
    for frame in frames:
        flowers = detect_flowers(frame, THRESHOLD)
        flowers = robust_sample(flowers, 3)  # how many flowers to click
        for (startX, startY, endX, endY) in flowers:
            # click on the center of the bounding box
            x = (startX + endX) // 2 + RECT.x
            y = endY + RECT.y - 5  # Adjusted y-coordinate
            #print(f'clicking on {x}, {y}')
            if do_click:
                pyautogui.click(x, y)
            if SHOW:
                color = (255, 0, 0)
                cv2.rectangle(frame, (startX, startY), (endX, endY), color, 3)  
        
        
        if RECORD:
            out.write(frame)

        if SHOW:
            for i, (startX, startY, endX, endY) in enumerate(flowers):
                # draw the bounding box on the image
                color = (0, 255, 0)
                cv2.rectangle(frame, (startX, startY), (endX, endY), color, 1)
            cv2.imshow("multigram", frame)
            if cv2.waitKey(waitkey_delay) & 0xFF == ord('q'):
                print('quit')
                break
        button = detect_button(frame,0.86)
        if button:
            print("Bottone trovato, numero = ")
            bottone+=1
            print(bottone)
            t = time.time()
            for (startX, startY, endX, endY) in button:
                x = (startX + endX) // 2 + RECT.x
                y = (startY + endY) //2 + RECT.y   # Adjusted y-coordinate
                if(bottone <= runs):
                    time.sleep(2)
                    pyautogui.click(x,y) 
                break
            
        if(bottone > runs or time.time()-t>60):
            print("finite le run:rompo il ciclo")
            break

    if out:
        out.release()
    quit(options)


               
def cmd_blum_all(options):
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 2 and not success:
            try:
                time.sleep(2)
                cmd_blum(options)
                cmd_blum(options)
                cmd_blum(options)

                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1
                quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_blum...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")
        
def cmd_blum_from_acc(options):
    start_from = 16
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(start_from,num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 5 and not success:
            try:
                time.sleep(2)
                cmd_farm(options)
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1
                exit_blum()
                exit_telegram()
                if attempts>2:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_blum...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")
