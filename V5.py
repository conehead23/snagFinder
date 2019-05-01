# All mine this time
# Damon Hill 30/04/19
# https://stream.massey.ac.nz/pluginfile.php/3195894/mod_resource/content/1/282762_notes.pdf
# https://stream.massey.ac.nz/pluginfile.php/3200807/mod_resource/content/1/Assessment%204%20-%20Machine%20Vision%20Assignment.pdf
# 

import cv2 as cv
import numpy as np
import math
import itertools

imgName = 'referenceImage.png'
window1 = 'Original Image'
window2 = 'Colour Thresholded Image'

lower = {'corn':(20, 200, 160), 'snag':(8,0,173), 'onions':(18,35,64)}      # define the lower and upper boundaries of the colors in the HSV color space
upper = {'corn':(30,255,255), 'snag':(19,59,234), 'onions':(56,206,255)}    # https://html-color-codes.info/colors-from-image/ or use V4
area = {'corn':10000,'snag':10000,'onions':30000}                           # minimum area of object in pixels
colors = {'corn':(0, 255, 217), 'snag':(0,140,255), 'onions':(56,206,255), 'black':(1,1,1), 'white':(255,255,255), 'red':(0,0,255)}

startCoord = (0,0)
centroidList = [startCoord]


def view_image(img):
    resizedImg = cv.resize(img, (1280,720))       # view a cv2 img
    cv.imshow(window1, resizedImg)
    cv.waitKey(0)
    cv.destroyAllWindows()


def draw_box(c):
    M = cv.moments(c)       # https://docs.opencv.org/3.4.3/dd/d49/tutorial_py_contour_features.html
    x = int(M["m10"] / M["m00"])
    y = int(M["m01"] / M["m00"])

    rect = cv.minAreaRect(c)
    box = cv.boxPoints(rect)
    box = np.int0(box)
    cv.drawContours(img, [box], 0, colors[key], 2, 16)  # draw bounding angled box
    cv.circle(img, (x, y), 10, colors['red'], -2)  # draw centeriod    https://www.learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    cv.putText(img, key + " at x" + str(round(x)) + ",y" + str(round(y)), (box[2][0], box[2][1] - 10),cv.FONT_HERSHEY_SIMPLEX, 1, colors[key], 2)  # draw object type and centroid location beside object
    #view_image(img)
    centroidList.append((x,y))


def cost(route):
    sum = 0
    # Go back to the start when done.
    route.append(route[0])
    while len(route) > 1:
        p0, *route = route
        sum += math.sqrt((int(p0[0]) - int(route[0][0]))**2 + (int(p0[1]) - int(route[0][1]))**2)
    return sum


img = cv.imread(imgName,1)                  # read img in BGR
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)    # convert to HSV colourspace
for key, value in lower.items():
    #view_image(hsv)
    mask = cv.inRange(hsv, lower[key], upper[key])      # create thresholded mask
    #view_image(mask)

    kernel = np.ones((12, 12), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)  # morphological transformations to remove noise
    #view_image(mask)
    openKernel = kernel = np.ones((9, 9), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN,openKernel)  # https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
    #view_image(mask)

    contours = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[-2]  # find contours in the mask and initialize the current (x, y) center of the ball
    if key == 'onions':
        c = max(contours, key=cv.contourArea)
        draw_box(c)
    else:
        for c in contours:
            cArea = cv.contourArea(c)
            print(cArea)
            if cArea < area[key]:
                continue
            draw_box(c)

print(centroidList)

# stolen from https://github.com/rshipp/tsp
d = float("inf")
for p in itertools.permutations(centroidList):      # https://docs.python.org/2/library/itertools.html#itertools.permutations
    if p[0] != startCoord:
        break
    c = cost(list(p))
    if c <= d:
        d = c
        pmin = p
print("Optimal route:", pmin)
print("Length:", d)
cv.putText(img,"Optimal route:"+str(pmin)+" Length:"+str(round(d))+"pixels", (100,1100),cv.FONT_HERSHEY_SIMPLEX, .8, colors['white'], 2)

i=0
end = len(pmin)
for point in pmin:
    i += 1
    if i == end:
        break
    cv.arrowedLine(img, point, pmin[i], colors['black'], 2,16)        # https://docs.opencv.org/master/d6/d6e/group__imgproc__draw.html#ga0a165a3ca093fd488ac709fdf10c05b2

cv.imwrite("Output.jpg", img)
view_image(img)
