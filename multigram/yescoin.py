
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
MINIAPP_RECT = Rect(x=255, y=100, w=385, h=694)
pyautogui. FAILSAFE = False


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
    log_file_name = "yescoin.txt"
    account_name = "placeholder"

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
            log_failure(i, account_name, log_file_name)
            print(f"Failed to process element {i} after 3 attempts.")

def start_chromium():

  
    
    workdir =  Path.cwd()
    workdir = workdir.joinpath('placeholder')

    launch_command(
    'chromium',
    f'--user-data-dir={shlex.quote(str(workdir))}',
    '--auto-open-devtools-for-tabs',
    f'--disk-cache-dir=/home/nicolo/chromium-cache2',  # Custom cache directory
    bg=True,
    redirect_null=False)
    time.sleep(3)

def quit_chromium():
  
    workdir = Path.cwd()
    workdir = workdir.joinpath('placeholder')

    launch_command('pkill', '-f', f"chromium.*--user-data-dir={str(workdir)}", bg=True, redirect_null=True)
        
        
def start_yescoin():
    
    wait_and_click('img/yescoinicon.png',timeout = 7)
    wait_and_click('img/yescoinlaunch.png', timeout=10)
    try:
        time.sleep(1)
        wait_and_click('img/OK.png',timeout =5)
    except Exception as e:
        pass
    time.sleep(10)
    swipe(MINIAPP_RECT, swipe_distance=300, duration=0.5)
    try:
        wait_and_click_confidence('img/xyes.png',timeout=20,confidence=0.7)
        wait_and_click_confidence('img/yessummer.png',timeout=10,confidence=0.7)
    except Exception as e:
        pass
    
def daily_yescoin():
    
    start_yescoin()
    time.sleep(2)
    wait_and_click_confidence('img/earn.png',timeout=20,confidence=0.8)
    daily_task()
    
def click_daily():
    
    time.sleep(4)

    try:
        wait_for_image_confidence('img/starty.png',confidence=0.7,timeout=5)
        time.sleep(5)
        print("start")
        pyautogui.click(x=444, y=669)
        time.sleep(5)
        print("check")
        pyautogui.click(x=450, y=709)
        time.sleep(5)
        print("claim")
        pyautogui.click(x=450, y=709)
        time.sleep(5)
        wait_and_click_confidence('img/lvup.png',timeout=5,confidence=0.7)

    except Exception as e:
        pass
    


def kill_chromium():
    
    current_directory = os.getcwd()

    # Construct the full path to kc.sh in the current directory
    kc_script_path = os.path.join(current_directory, 'kc.sh')

    # Launch kc.sh script in the current directory
    launch_command(kc_script_path, bg=True, redirect_null=False)

def daily_task():
    wait_for_image_confidence('img/task.png',timeout=20,confidence=0.7)

    pyautogui.click(x=405, y=504) #first quest
    print("first task")
    click_daily()
    pyautogui.click(x=429, y=581) #second quest
    print("second task")
    click_daily()
    pyautogui.click(x=446, y=676) #third quest
    print("third task")
    click_daily()
    scroll_mid_screen(MINIAPP_RECT)
    pyautogui.click(x=433, y=430) #fourth quest
    click_daily()
    pyautogui.click(x=433, y=430) #fifth quest
    kill_chromium()


        
def cmd_ysetup(options):
    cmd_start(options)
    daily_yescoin()
    quit(options)
    
def cmd_ysetup_all(options):
    account_name = "placeholder"
    log_file_name = "yescoinsetup.txt"

    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 3 and not success: #farm isn't that relevant be fast
            try:
                time.sleep(2)
                cmd_ysetup(options)
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1 
                exit_blum()
                exit_telegram()
                if attempts>0:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_check...")

        if not success:
            log_failure(i, account_name, log_file_name)

            print(f"Failed to process element {i} after 3 attempts.")
    
def find_check():
 try:
    wait_and_click_confidence('img/check.png',confidence=0.9,timeout=5)
 except Exception as e:
    scroll_mid_screen(MINIAPP_RECT)
       
    wait_and_click_confidence('img/check.png',confidence=0.9,timeout=5)
    
def cmd_check_in(options) :
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
    start_yescoin()
    wait_and_click_confidence('img/earn.png',timeout=20,confidence=0.7)
    find_check()

    try:
        time.sleep(2)

        wait_and_click_confidence('img/starty.png',confidence=0.9,timeout=5)
        time.sleep(2)
    except Exception as e :
        wait_and_click_confidence('img/startpurple.png',confidence=0.9,timeout=5)

    wait_and_click_confidence('img/get_it.png',timeout=20,confidence=0.7)
    time.sleep(3)
    wait_and_click_confidence('img/yesclaim.png',timeout=20,confidence=0.7) 
    time.sleep(3)

    wait_and_click_confidence('img/yesclaim2.png',timeout=20,confidence=0.7) 
    time.sleep(3)

    wait_and_click_confidence('img/yesdone.png',timeout=20,confidence=0.7) 
    time.sleep(3)

    wait_and_click_confidence('img/return.png',timeout=20,confidence=0.7) 
    find_check()
    time.sleep(5)

    print("check")
    pyautogui.click(x=450, y=709)
    time.sleep(5)
    print("claim")
    pyautogui.click(x=450, y=709)
    wait_and_click_confidence('img/lvup.png',timeout=2,confidence=0.7)

    time.sleep(3)
    quit(options)
def cmd_check_in_all(options):
    account_name = "placeholder"
    log_file_name = "yescoincheck.txt"

    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 3 and not success: #farm isn't that relevant be fast
            try:
                time.sleep(2)
                cmd_check_in(options)
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1 
                exit_blum()
                exit_telegram()
                if attempts>0:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_check...")

        if not success:
            log_failure(i, account_name, log_file_name)

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
