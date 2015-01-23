#!/usr/bin/python2

import numpy as np
import cv2
import sys

def transformImage(corners, result):
    if(len(corners) != 4):
        print("Not a square!")
        print("{} Corners".format(len(corners)))
        return None

    center = [0,0]
    for corner in corners:
        center[0] += corner[0]
        center[1] += corner[1]
    center[0] *= (1./len(corners))
    center[1] *= (1./len(corners))

    top = []
    bot = []

    for corner in corners:
        if corner[1] < center[1]:
            top.append(corner)
        else:
            bot.append(corner)

    if len(bot) != 2 or len(top) != 2:
        print("Found error in picture, continuing to next element...")
        return None, result

    tl = top[1] if top[0][0] > top[1][0] else top[0]
    tr = top[0] if top[0][0] > top[1][0] else top[1]
    bl = bot[1] if bot[0][0] > bot[1][0] else bot[0]
    br = bot[0] if bot[0][0] > bot[1][0] else bot[1]

    corners = []
    corners.append(tl)
    corners.append(tr)
    corners.append(bl)
    corners.append(br)

    #Ajust for cards laying down
    if (tr[0] - tl[0]) > (bl[1] - tl[1]):
        result = (result[1], result[0])

    dst_corners = []
    dst_corners.append([0,0])
    dst_corners.append([result[0],0])
    dst_corners.append([0, result[1]])
    dst_corners.append([result[0],result[1]])
    return cv2.getPerspectiveTransform(np.asarray(corners, np.float32),np.asarray(dst_corners,np.float32)), result

def findRect(imgray, verbose = False):

    ret, thresh = cv2.threshold(imgray, 127,255,0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnt = contours[1]
    if verbose:
        im = cv2.cvtColor(imgray, cv2.COLOR_GRAY2RGB)

        for contour in contours:
            cv2.drawContours(im, [contour], 0, (0,255,0), 2)
        cv2.drawContours(im, [cnt], 0, (0,0,255),1)
        cv2.imshow("Contours", im)

    mask = np.zeros(imgray.shape, np.uint8)
    cv2.drawContours(mask, [cnt], 0,255,-1)

    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    return box

#Takes an image and finds all the level 0 contours on it, after that it draws a square around them, and returns those in an array
def findMultipleRects(imgray, verbose = False):
    ret, thresh = cv2.threshold(imgray, 127,255,0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if verbose:
        print("Contours found")
    cnts = []

    #Find all the level 0 contours and add them to 'cnts'
    for i in range(len(contours)):
        if hierarchy[0][i][3] == 0:
            if verbose:
                print("Accepted contour: {0}".format(hierarchy[0][i]))
            cnts.append(contours[i])

    if verbose:
        print("Creating boxes")
    boxes = []
    #Draw boxes around the contours, and add the boxes to 'boxes'
    for cnt in cnts:
        rect = cv2.minAreaRect(cnt)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        boxes.append(box)
    return boxes

if __name__ == "__main__":

    cv2.namedWindow("Start", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
    im = cv2.imread(sys.argv[1])
    imgray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    cv2.imshow("Start", im)
    boxes = findMultipleRects(imgray)
    for box in boxes:
        cv2.drawContours(im, [box], 0, (0,0,255),5)
    cv2.imshow("Result", im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
