# Find your colour threshold values
# Stolen from https://docs.opencv.org/master/da/d97/tutorial_threshold_inRange.html
# Adjusted by Damon Hill, 30/04/19


import cv2 as cv

imgName = 'referenceImage.png'
max_value = 255
max_value_H = 360 // 2
low_H = 0
low_S = 0
low_V = 0
high_H = max_value_H
high_S = max_value
high_V = max_value
window_capture_name = 'Original Image'
window_detection_name = 'Colour Thresholded Image'
low_H_name = 'Low H'        # 20    8       18
low_S_name = 'Low S'        # 200   0       35
low_V_name = 'Low V'        # 160   173     64
high_H_name = 'High H'      # 30    19      56
high_S_name = 'High S'      # 255   59      206
high_V_name = 'High V'      # 255   234     255


def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H - 1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)


def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H + 1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)


def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S - 1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)


def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S + 1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)


def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V - 1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)


def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V + 1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)


img = cv.imread(imgName,1)                  # read img in BGR
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)    # convert to HSV colourspace

cv.namedWindow(window_capture_name)         # make windows
cv.namedWindow(window_detection_name)

cv.createTrackbar(low_H_name, window_detection_name, low_H, max_value_H, on_low_H_thresh_trackbar)      # make bars
cv.createTrackbar(high_H_name, window_detection_name, high_H, max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name, low_S, max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name, high_S, max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name, low_V, max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name, high_V, max_value, on_high_V_thresh_trackbar)

while True:
    frame_threshold = cv.inRange(hsv, (low_H, low_S, low_V), (high_H, high_S, high_V))      # create thresholded mask


    cv.imshow(window_capture_name, frame_threshold)     # display original img
    #frame_threshold = cv.resize(frame_threshold, (1333, 1000))
    cv.imshow(window_detection_name, frame_threshold)       #display thresholded img

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:        # repeat until window is exited
        break