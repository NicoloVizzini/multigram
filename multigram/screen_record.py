import time
import cv2
import numpy as np
import mss

def capture_screen(rect, show_fps=True):
    last_time = 0
    with mss.mss() as sct:
        #monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
        monitor = {"top": rect.y, "left": rect.x, "width": rect.w, "height": rect.h}
        while True:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            # Convert from BGRA to BGR (cv2 uses BGR by default)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            if show_fps:
                fps = 1 / (time.time() - last_time)
                cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            yield frame
            last_time = time.time()
