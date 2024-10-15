
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







def start_yescoin():
    wait_and_click('img/yescoinicon.png',timeout = 7)
    wait_and_click('img/yescoinlaunch.png', timeout=10)
    try:
        time.sleep(0.51)
        wait_and_click('img/OK.png',timeout =5)
    except Exception as e:
        pass

def cmd_set_yescoin(options):
        cmd_start(options)
        time.sleep(5)
        pyautogui.write("yescoin")
        time.sleep(2)
        pyautogui.click(x=145, y=146)
        time.sleep(2)
        pyautogui.click(x=602, y=863)
        time.sleep(2)
        pyautogui.click(x=364, y=870)    
        try:
            time.sleep(0.5)
            wait_and_click('img/OK-MD.png',timeout =5)
        except Exception as e:
            pass
        time.sleep(10)
        quit(options)
        
def cmd_set_yescoin_all(options):
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 3 and not success: #farm isn't that relevant be fast
            try:
                time.sleep(2)
                cmd_set_yescoin(options)
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

def cmd_check(options) :
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
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



    
def exit_blum():
    pyautogui.hotkey('alt', 'f4')

def exit_telegram():
    pyautogui.hotkey('alt', 'f4')


    



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
