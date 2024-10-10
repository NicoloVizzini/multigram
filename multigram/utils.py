import os
import subprocess
import time
import itertools
import pyautogui
from tqdm import tqdm
import cv2
import numpy as np
import sys
import shlex
from dataclasses import dataclass
from pathlib import Path
from docopt import docopt
from wmctrl import Window
from .screen_record import capture_screen
import random







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
def wait_for_image(img, *, timeout):
    """
    Wait img appears on screen, until timeout.
    Return the location.
    """
    progress = tqdm(
        desc=f'Locating {img}',
        unit='s',
        total=timeout,
        bar_format='{desc} [{n:.2f}/{total:.2f} s] {bar}'
    )
    start = time.time()
    with progress:
        i = 0
        while True:
            elapsed = time.time() - start
            progress.update(int(elapsed) - progress.n)
            if elapsed >= timeout:
                raise pyautogui.ImageNotFoundException(img)
            try:
                return pyautogui.center(pyautogui.locateOnScreen(img))
            except pyautogui.ImageNotFoundException:
                pass

def wait_and_click(img, *, timeout=0):
    """
    Same as wait_for_image, but also click on the image as soon as it's found.
    """
    p = wait_for_image(img, timeout=timeout)
    pyautogui.click(p)


def get_screen_resolution():
    # Run xrandr command to get screen information
    output = subprocess.run(['xrandr'], capture_output=True, text=True).stdout

    # Find the line containing the screen resolution
    for line in output.splitlines():
        if '*' in line:  # The current resolution line contains '*'
            resolution = line.split()[0]  # Get the resolution (first column)
            width, height = map(int, resolution.split('x'))
            return width, height

    return None  # In case resolution is not found

def set_cv2_DISPLAY(display=":0"):
    """
    This is a hack.

    We want to use two DISPLAYs:

      - one for pyautogui and mss, which is the Xephyr window
      - one for opencv, which is our main X11 (for development)

    Ideally, I would like cv2.imshow("...", img, DISPLAY=":0") but there is no
    way to pass DISPLAY to imshow.

    The hack is to temporarily change DISPLAY, open and close a small cv2
    window, and then reset DISPLAY to the old value. This way, cv2 "remembers"
    the desired value of DISPLAY and next invocations of imshow will use it.
    """
    
    old = os.environ['DISPLAY']
    os.environ['DISPLAY'] = display
    try:
        img = np.zeros((1, 1, 3), dtype=np.uint8)
        cv2.imshow('dummy image', img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()
    finally:
        os.environ['DISPLAY'] = old

if __name__ == '__main__':
    resolution = get_screen_resolution()
    if resolution:
        print(f"Screen resolution: {resolution[0]}x{resolution[1]}")
    else:
        print("Unable to determine screen resolution.")

















    
def change_ACCOUNTS(options):
    if options['--folder'] is not None:
        folder_name = options['--folder']
        global ACCOUNTS
        ACCOUNTS = ROOT.joinpath(folder_name)
        return ACCOUNTS
    
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
    time.sleep(1)
    scroll_mid_screen(rect)
    time.sleep(0.2)
    
def launch_command(*args, bg=False, redirect_null=False):
    cmdline = [shlex.quote(arg) for arg in args]
    cmdline = ' '.join(cmdline)
    if redirect_null:
        cmdline += ' > /dev/null 2>&1'
    if bg:
        cmdline += ' &'
    print(f'EXEC: {cmdline}')
    return os.system(cmdline)


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
    change_ACCOUNTS(options)
    accounts, not_accounts = get_accounts()
    for name in accounts:
        print(name)

    if not_accounts:
        print('The following seems to be invalid accounts:')
        for name in not_accounts:
            print(name)

def cmd_start(options):
    change_ACCOUNTS(options)
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

def count_elements_in_directory(directory):
    # List all entries in the directory
    entries = os.listdir(directory)
    return len(entries)

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
