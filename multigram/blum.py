import sys
import cv2
import numpy as np


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



