"""
Multigram - multiple telegram instances

usage:
    multigram.py <command> [options]

options:
    -h, --help                  shows the help
    -a, --account=NAME          name of the account to launch
    -c, --create                create a new account if it doesn't exist
    -n, --number=<number>       number of the account you want to launch
    -f, --folder = <folder>     specify the folder that contains the accounts
    --no-redirect               don't redirect stdout/stderr
    --video                     use video file instead of screen capture
    --dont-click                don't click on the screen
    --record=FILE               record a video to FILE while playing
    --step                      step through the video frame by frame
Available commands:
    list                        list all available acconuts
    start                       launch a new telegram instance
    screenshot                  take a screenshot of the telegram window
    screen_record               record the miniapp window
    blum                        play blum
    blum_all  play blum on all accounts
    blum_from_acc
    rectsel                     select a rectangle on the screen
    check                       does the check in
    check_all                   does the check in in all accounts
    farm                        does the farm
    farm_all                    does the farm on all accounts
    money_setup
    money_setup_all
    set_yescoin             
    set_yescoin_all
"""

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
from .utils import wait_and_click, wait_for_image, set_cv2_DISPLAY
from .screen_record import capture_screen
from .blum import *
from .moneydogs import *
from .yescoin import cmd_set_yescoin, cmd_set_yescoin_all
import random
import numpy as np
import subprocess



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


def main():
    set_cv2_DISPLAY(":0")
    options = docopt(__doc__)
    command = options.pop('<command>')
    if command == 'list':
        cmd_list(options)
    elif command == 'start':
        cmd_start(options)
    elif command == 'screenshot':
        cmd_screnshot(options)
    elif command == 'screen_record':
        cmd_screen_record(options)
    elif command == 'check':
        cmd_check(options)
    elif command == 'check_all':
        cmd_check_all(options)
    elif command == 'farm':
        cmd_farm(options)
    elif command == 'farm_all':
        cmd_farm_all(options)
    elif command == 'blum':
        cmd_blum(options)
    elif command == 'blum_all':
        cmd_blum_all(options)
    elif command == 'rectsel':
        cmd_rectsel(options)
    elif command == 'blum_from_acc':
        cmd_blum_from_acc(options)
    elif command == 'money_setup':
        cmd_money_setup(options)
    elif command == 'money_setup_all':
        cmd_money_setup_all(options)
    elif command == 'set_yescoin':
        cmd_set_yescoin(options)
    elif command == 'set_yescoin_all':
        cmd_set_yescoin_all(options)
    else:
        print(f'Invalid command: {command}')
        print(__doc__)
        sys.exit(1)
        


if __name__ == '__main__':
    main()
