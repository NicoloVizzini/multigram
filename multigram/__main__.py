"""
Multigram - multiple telegram instances

usage:
    multigram.py <command> [options]

options:
    -h, --help                  shows the help
    -a, --account=NAME          name of the account to launch
    -c, --create                create a new account if it doesn't exist
    -n, --number=<number>       number of the account you want to launch
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
    blum_all                    play blum on all accounts
    rectsel                     select a rectangle on the screen
    check                       does the check in
    check_all                   does the check in in all accounts
    farm                        does the farm
    farm_all                    does the farm on all accounts
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
from .blum import detect_flowers, detect_button
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
MINIAPP_RECT = Rect(x=259, y=104, w=398, h=705)


def scroll_mid_screen(rect):
    """
    Scroll down in the middle of the Telegram window to ensure that the content
    is fully visible.
    """
    mid_x = rect.x + rect.w // 2
    mid_y = rect.y + rect.h // 2
    pyautogui.moveTo(mid_x, mid_y)
    print("Scroll down")
    pyautogui.scroll(-500)  # Scroll down
    
    
    
def wait_for_scroll(img,rect):
    wait_for_image(img,timeout=10)
    scroll_mid_screen(rect)
    
def launch_command(*args, bg=False, redirect_null=False):
    cmdline = [shlex.quote(arg) for arg in args]
    cmdline = ' '.join(cmdline)
    if redirect_null:
        cmdline += ' > /dev/null 2>&1'
    if bg:
        cmdline += ' &'
    print(f'EXEC: {cmdline}')
    return os.system(cmdline)

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
    else:
        print(f'Invalid command: {command}')
        print(__doc__)
        sys.exit(1)
        
def get_accounts():
    accounts = []
    not_accounts = []
    for child in ACCOUNTS.iterdir():
        is_account = child.joinpath('tdata').exists()
        if is_account:
            accounts.append(child.name)
        else:
            not_accounts.append(child.name)
    accounts.sort()
    not_accounts.sort()
    return accounts, not_accounts
    

def cmd_list(options):
    accounts, not_accounts = get_accounts()
    for name in accounts:
        print(name)

    if not_accounts:
        print('The following seems to be invalid accounts:')
        for name in not_accounts:
            print(name)

def cmd_start(options):
    account = options['--account']
    account_number = options['--number']
    if account is None and account_number is None:
        print('Please specify an account with -a or --account or the number of the account with -n or --number')
        sys.exit(1)
    
    if options['--account']:
       print(options['--account'])
       workdir = ACCOUNTS.joinpath(account)
    else:

        account_dirs = sorted([account for account in ACCOUNTS.iterdir() if account.is_dir()])
        position = int(options['--number'])
        print(position)
        if len(account_dirs) > position :
            account = account_dirs[position]
            account_name = account.name  # Get the final name of the folder
            options['--account'] = account.name
            workdir = ACCOUNTS.joinpath(account)
        else:
             print('Please use -a or --account and then --create to automatically create a new one')
             sys.exit(1)

    if not workdir.exists():
        print(f'Account {account} does not exist')
        if options['--create']:
            print('Creating a new one...')
        else:
              print('Please use --create to automatically create a new one')
              sys.exit(1)
    launch_command(
        TELEGRAM,
        '-workdir', str(workdir),
        bg=True,
        redirect_null=not options['--no-redirect'])
    #reposition_telegram()
    

    
def quit(options):
    account = options['--account']
    print(account)
    workdir = ACCOUNTS.joinpath(account)
    launch_command(
    TELEGRAM,
    '-workdir', str(workdir),'-quit',
    bg=True,
    redirect_null=not options['--no-redirect'])
    print(f'Telegram for account {account} has been quit.')
    options ['--account'] = None

        
'''        
def reposition_telegram():
    """
    Wait until the active window is a telegram one, then reposition it to a
    top-left corner.
    """
    def find_window():
        for i in range(10):
            w = Window.get_active()
            print(f'[WINDOW] active window is {w.wm_name} - {w.wm_class}')
            if w.wm_class == 'Telegram.TelegramDesktop':
                print('[WINDOW] found!')
                return w
            else:
                time.sleep(0.5)
        else:
            print('[WINDOW] telegram not found, aborting')
            sys.exit(1)

    win = find_window()
    R = TELEGRAM_RECT
    win.resize_and_move(x=R.x, y=R.y, w=R.w, h=R.h)
'''
def cmd_screnshot(options):
   telegram_screenshot('/home/nicolo/tg.png')

def telegram_screenshot(filename=None):
    R = TELEGRAM_RECT

    os.system(f'import -window root -crop {R.w}x{R.h}+{R.x}+{R.y} {filename}')
    if filename:
        print(f'[SCREENSHOT] saved to {filename}')


def cmd_screen_record(options):
    RECT = MINIAPP_RECT
    video_file = "screencast.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_file, fourcc, 20.0, (RECT.w, RECT.h))
    for frame in capture_screen(RECT, show_fps=True):
        out.write(frame)
        cv2.imshow("multigram", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()
    cv2.destroyAllWindows()

def cmd_rectsel(options):
    from xrectsel import XRectSel
    xrect = XRectSel()
    r = xrect.select()
    r2 = Rect(x=r['start']['x'], y=r['start']['y'], w=r['width'], h=r['height'])
    print(r2)

def myclick(filename, sleep_after=0):
    #print(f'clicking on {filename}...', end='')
    sys.stdout.flush()
    pyautogui.click(filename)
    if sleep_after:
        time.sleep(sleep_after)
    print(' DONE')

def robust_sample(lst, k):
    if len(lst) < k:
        return lst
    indices = np.random.choice(len(lst), k, replace=False)
    return [lst[i] for i in indices]


def cmd_check(options) :
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
    wait_and_click('img/blum-icon.png',timeout = 7)
    wait_and_click('img/blum-launchx.png', timeout=10)
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
                if attempts>1:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_check...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")


def cmd_farm(options):
    
    cmd_start(options)
    wait_and_click('img/blum-icon.png',timeout = 7)
    wait_and_click('img/blum-launchx.png', timeout=10)
    wait_and_click('img/blum-farm2.png', timeout=10)
    try:
        wait_and_click('img/startfarmtribe.png',timeout=10)
    except Exception as e:
        wait_and_click('img/startfarm.png',timeout=10)
    time.sleep(1)
    quit(options)
           

def cmd_farm_all(options):
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
                if attempts>1:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_farm...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")
   

    
def exit_blum():
    pyautogui.hotkey('alt', 'f4')

def exit_telegram():
    pyautogui.hotkey('alt', 'f4')


def cmd_blum(options):
    runs = 8
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
        wait_and_click('img/blum-icon.png',timeout = 7)
        wait_and_click('img/blum-launchx.png', timeout=10)
        wait_for_scroll ('img/waitforblum.png',MINIAPP_RECT)
        wait_and_click('img/blum-play2.png',timeout = 10)
        frames = capture_screen(RECT, show_fps=True)

    if SHOW:
        cv2.namedWindow("multigram")
        cv2.createTrackbar("Threshold", "multigram", int(THRESHOLD * 100), 100, on_threshold_change)

    for i in range(runs):
        print("here")
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
            if time.time() - t > 30:
                    try:
                        button = detect_button(frame,0.8)
                        for (startX, startY, endX, endY) in button:
                            x = (startX + endX) // 2 + RECT.x
                            y = (startY + endY) //2 + RECT.y   # Adjusted y-coordinate
                        pyautogui.click(x,y)
                        break
                    except Exception as e:
                            pyautogui.moveTo(1,1) #

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

    if out:
        out.release()
    quit(options)


def count_elements_in_directory(directory):
    # List all entries in the directory
    entries = os.listdir(directory)
    return len(entries)

   
            
               
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
                success = True  # If cmd_blum runs successfully, set success to True
            except Exception as e:
                attempts += 1
                exit_blum()
                exit_telegram()
                if attempts>1:
                    quit(options)
                print(f"Attempt {attempts} of 5. Restarting cmd_blum...")

        if not success:
            print(f"Failed to process element {i} after 3 attempts.")
        
def cmd_blum_from_acc(options):
    num_elements = count_elements_in_directory(ACCOUNTS)
    for i in range(num_elements):
        options['--number'] = str(i)
        attempts = 0
        success = False
        
        while attempts < 5 and not success:
            try:
                time.sleep(2)
                cmd_blum(options)
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
def read_video(filename, infinite=False):
    cap = cv2.VideoCapture(filename)
    while True:
        ret, frame = cap.read()
        if not ret:
            if infinite:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break
        yield frame
    cap.release()


if __name__ == '__main__':
    main()
