# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 17:09:50 2019

@author: Carl
"""

import cv2
import numpy as np

corn_l = np.array([21, 145, 238])
corn_h = np.array([37, 255, 255])

scaling_factor = float(0.5)
img = cv2.imread('food.png', 1)
img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
threshold_area = 10000
green = (124,252,0)
red = (0,0,255)
blue = (220,20,60)
purple = (138,43,226)



def find_objects(thresholded_image, min_area):
    a, conts ,h = cv2.findContours(thresholded_image.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    conts2 = []  
    for cnt in conts:       
        area = cv2.contourArea(cnt)         
        if area > threshold_area:
            conts2.append(cnt)
    return conts2       
    

def threshold_image(image):
    blur = cv2.GaussianBlur(image,(15,15),0)
    img2 = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    ret, img2 = cv2.threshold(img2,0,250,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return img2

def draw_rectangles(objects, colour):    
    for i in range(len(objects)):
        x,y,w,h=cv2.boundingRect(objects[i])
        cv2.rectangle(img,(x,y),(x+w,y+h),colour, 2)    

def draw_ellipses(objects, colour, img): 
    for i in objects:
         ellipse = cv2.fitEllipse(i)
         cv2.ellipse(img,ellipse,colour,2)
    return img
         
def remove_largest_width(objects) :
    widths = []
    filtered = []
    largest = []
    for item in objects:
        x,y,w,h = cv2.boundingRect(item)
        widths.append(w)
    for item in objects:
        x,y,w,h = cv2.boundingRect(item)
        if w != max(widths):
            filtered.append(item)
        else:
            largest.append(item)
    return filtered, largest
     
thresh_all = threshold_image(img)

all_items = find_objects(thresh_all, threshold_area)

sausages_and_corn, onion = remove_largest_width(all_items) 
sausages, corn = remove_largest_width(sausages_and_corn)

img2 = draw_ellipses(sausages, blue, img)
#draw_ellipses(corn, green)
#draw_ellipses(onion, red)

moments = all_items[0]

x_centres = []
y_centres = []
for i in range(len(all_items)):
    moments = cv2.moments(all_items[i])
    x_centres.append(int(moments['m10']/moments['m00']))
    y_centres.append(int(moments['m01']/moments['m00']))
    #cv2.line(img,(0,0),(x_centres[i],y_centres[i]), purple, 2)

cv2.imshow("Processed Image", img2)

cv2.waitKey(10)
