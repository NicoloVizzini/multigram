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
    screen_record               record the telegram window
    blum                        play blum
    rectsel                     select a rectangle on the screen
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

from .screen_record import capture_screen
from .blum import detect_flowers
import random
import numpy as np

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

TELEGRAM_RECT = Rect(x=64, y=0, w=1000, h=1300)
MINIAPP_RECT = Rect(x=304, y=160, w=520, h=820)

def scroll_mid_screen(rect):
    """
    Scroll down in the middle of the Telegram window to ensure that the content
    is fully visible.
    """
    mid_x = rect.x + rect.w // 2
    mid_y = rect.y + rect.h // 2
    pyautogui.moveTo(mid_x, mid_y)
    pyautogui.scroll(-500)  # Scroll down

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
    return accounts, not_accounts

def cmd_list(options):
    accounts, not_accounts = get_accounts()
    accounts.sort()
    not_accounts.sort()
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
        workdir = ACCOUNTS.joinpath(account)
    else:
        account_dirs = sorted([account for account in ACCOUNTS.iterdir() if account.is_dir()])
        position = int(options['--number'])
        if len(account_dirs) > position :
            account = account_dirs[position]
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
    reposition_telegram()
    

    

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
    print(f'clicking on {filename}...', end='')
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


def check_in() :
    time.sleep(3)
    pyautogui.write("blum")
    pyautogui.press('enter')
    myclick('img/blum-launch2.png', sleep_after=5)
    time.sleep(10)
    pyautogui.hotkey('alt', 'f4')
     
def exit_blum():
    pyautogui.hotkey('alt', 'f4')

def exit_telegram():
    pyautogui.hotkey('alt', 'f4')

def cmd_blum(options):
    runs = 2
    RECT = MINIAPP_RECT
    THRESHOLD = 0.66
    SHOW = False
    cmd_start(options)
    time.sleep(6)
    check_in()
    time.sleep(2)
   

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
        x, y = pyautogui.position()  # Get current mouse position
        pyautogui.click(x, y)  # Click at the current position       
        time.sleep(5)
        scroll_mid_screen(MINIAPP_RECT)
        time.sleep(0.5)
        myclick('img/blum-play2.png')
        frames = capture_screen(RECT, show_fps=True)

    if SHOW:
        cv2.namedWindow("multigram")
        cv2.createTrackbar("Threshold", "multigram", int(THRESHOLD * 100), 100, on_threshold_change)

    for i in range(runs):
        t = time.time()
        for frame in frames:
            flowers = detect_flowers(frame, THRESHOLD)
            flowers = robust_sample(flowers, 3)  # how many flowers to click
            for (startX, startY, endX, endY) in flowers:
                # click on the center of the bounding box
                x = (startX + endX) // 2 + RECT.x
                y = endY + RECT.y - 5  # Adjusted y-coordinate
                print(f'clicking on {x}, {y}')
                if do_click:
                    pyautogui.click(x, y)
                if SHOW:
                    color = (255, 0, 0)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 3)

            if time.time() - t > 55:
                if i!= runs-1:
                    pyautogui.position(0,0)
                    myclick('img/blum-play-again2.png', sleep_after=0)

                break
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
    exit_blum()
    exit_telegram()

def count_elements_in_directory(directory):
    # List all entries in the directory
    entries = os.listdir(directory)
    return len(entries)




def cmd_blum_all(options):
   num_elements = count_elements_in_directory(ACCOUNTS)
   for i in range(num_elements):
        options['--number'] = str(i)
        cmd_blum(options) 
    
        
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
