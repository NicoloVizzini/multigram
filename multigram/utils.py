import os
import subprocess
import time
import itertools
import pyautogui
from tqdm import tqdm
import cv2
import numpy as np

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
