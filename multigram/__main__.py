"""
Multigram - multiple telegram instances

usage:
    multigram.py <command> [options]

options:
    -h, --help                  shows the help
    -a, --account=NAME          name of the account to launch [default: main]
    -c, --create                create a new account if it doesn't exist
    --no-redirect               don't redirect stdout/stderr
    --video                     use video file instead of screen capture

Available commands:
    list                        list all available acconuts
    start                       launch a new telegram instance
    screenshot                  take a screenshot of the telegram window
    screen_record               record the telegram window
    blum                        develop the blum algorithm
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
    elif command == 'dev':
        cmd_dev(options)
    else:
        print(f'Invalid command: {command}')
        print(__doc__)
        sys.exit(1)

def cmd_list(options):
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
    for name in accounts:
        print(name)

    if not_accounts:
        print('The following seems to be invalid accounts:')
        for name in not_accounts:
            print(name)

def cmd_start(options):
    account = options['--account']
    workdir = ACCOUNTS.joinpath(account)
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
    telegram_screenshot('/tmp/telegram.png')

def telegram_screenshot(filename=None):
    R = TELEGRAM_RECT

    os.system(f'import -window root -crop {R.w}x{R.h}+{R.x}+{R.y} {filename}')
    if filename:
        print(f'[SCREENSHOT] saved to {filename}')


def cmd_screen_record(options):
    video_file = "screencast.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_file, fourcc, 20.0, (TELEGRAM_RECT.w, TELEGRAM_RECT.h))
    for frame in capture_screen(TELEGRAM_RECT, show_fps=True):
        out.write(frame)
        cv2.imshow("multigram", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()
    cv2.destroyAllWindows()


def cmd_blum(options):
    THRESHOLD = 0.5

    def on_threshold_change(value):
        nonlocal THRESHOLD
        THRESHOLD = value / 100

    cv2.namedWindow("multigram")
    cv2.createTrackbar("Threshold", "multigram", int(THRESHOLD * 100), 100, on_threshold_change)

    if options['--video']:
        frames = read_video("screencast.mp4", infinite=True)
        do_click = False
    else:
        frames = capture_screen(TELEGRAM_RECT, show_fps=True)
        do_click = True

    for frame in frames:
        pick = detect_flowers(frame, THRESHOLD)
        #pick = detect_green_sprites(frame)
        for (startX, startY, endX, endY) in pick:
            # draw the bounding box on the image
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          (255, 0, 0), 3)

            if do_click:
                # click on the center of the bounding box
                x = (startX + endX) // 2
                y = (startY + endY) // 2
                # transform the coordinates to the screen
                pyautogui.click(x + TELEGRAM_RECT.x, y + TELEGRAM_RECT.y)

        # show the output image
        cv2.imshow("multigram", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

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
