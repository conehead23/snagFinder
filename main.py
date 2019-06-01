import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, qRgb
import cv2
import numpy as np
from imutils import perspective
from scipy.spatial import distance as dist

gray_color_table = [qRgb(i, i, i) for i in range(256)]

def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                return qim.copy() if copy else qim

img = cv2.imread("food.png", 1)
img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img3 = img2.copy()

height, width, channels = img.shape

threshold_area = height*width/300
green = (124,252,0)
blue = (0,0,255)
red = (220,20,60)
purple = (75,0,130)
black = (0,0,0)
light_purple = (138,43,226)

def find_objects(thresholded_image, min_area):
    a, conts ,h = cv2.findContours(thresholded_image.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    conts2 = []
    widths = []
    
    for cnt in conts:       
        area = cv2.contourArea(cnt)         
        if area > threshold_area:
            conts2.append(cnt)
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = perspective.order_points(box)
        # order the points in the contour such that they appear
        #in top-left, top-right, bottom-right, and bottom-left order
            (tl, tr, br, bl) = box

            D = dist.euclidean(tl, tr)
            D1 = dist.euclidean(tl, bl)
            if D < D1:
                widths.append(D)
            else:
                widths.append(D1)
        
    return conts2, widths       
    

def threshold_image(image):
    blur = cv2.GaussianBlur(image,(15,15),0)
    cv2.imwrite("Gaussian.png",blur)
    image2 = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    ret, image2 = cv2.threshold(image2,0,250,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return image2

def draw_ellipses(objects, colour, image): 
    for i in objects:
         ellipse = cv2.fitEllipse(i)
         cv2.ellipse(image,ellipse,colour,4)
    return image
         
def draw_lines(objects, colour, image):
    for i in range(0, len(objects), 2):
        if i == 0:
            cv2.line(image, (0,0), (objects[i], objects[i+1]), colour, 4)
        elif i+1 < len(objects)-1:
            cv2.line(image, (objects[i-2], objects[i-1]), (objects[i], objects[i+1]), colour, 4)
        else:
            cv2.line(image, (objects[i-2], objects[i-1]), (objects[i], objects[i+1]), colour, 4)
            cv2.line(image, (objects[i], objects[i+1]), (0,0), colour, 4)
    return image       

def filter_by_width(objects, widths) :
    sausage = []
    corn = []
    onion = []
    for i in range(0, len(widths)):
        w = widths[i]
        if w <= width/10:
            sausage.append(objects[i])
        elif w > width/10 and w < width/6:
            corn.append(objects[i])
        else:
            onion.append(objects[i])     
    return sausage, onion, corn



thresh_all = threshold_image(img)

all_items, widths = find_objects(thresh_all, threshold_area)

sausages, onion, corn = filter_by_width(all_items, widths)

class ObjectDetection(QDialog):
    def __init__(self):
        super(ObjectDetection,self).__init__()
        loadUi('ObjectDetection.ui',self)
        self.setWindowTitle('Food Finder')
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_2.clicked.connect(self.on_pushButton_2_clicked)
        self.pushButton_3.clicked.connect(self.on_pushButton_3_clicked)
        self.pushButton_4.clicked.connect(self.on_pushButton_4_clicked)
        self.pushButton_5.clicked.connect(self.on_pushButton_5_clicked)
        self.pushButton_6.clicked.connect(self.on_pushButton_6_clicked)
        self.img = None
        self.pixelmap = None
        self.objects = all_items
        self.x_c = []
        self.y_c = []
        self.route = []
        self.skip_x = []
        self.skip_y = []
        self.root_dist = 0
        self.width = self.label.frameGeometry().width()
        self.height = self.label.frameGeometry().height()
        
        #self.resize(pixmap.width(), pixmap.height())
    @pyqtSlot()
    def find_route_length(self, points):
        d = 0
        for i in range(0, len(points), 2):
            if i == 0:
                d += dist.euclidean((0,0), (points[i], points[i+1]))
            elif i+1 < len(points)-1:
                d += dist.euclidean((points[i-2], points[i-1]), (points[i], points[i+1]))
            else:
                d += dist.euclidean((points[i-2], points[i-1]), (points[i], points[i+1]))
                d += dist.euclidean((points[i], points[i+1]), (0,0))
        return d
    
    def solve_segment(self, x_points, y_points, curent_segment):
        quart_width = width/4
        next_seg = 0
        if len(x_points) == 0:
                return 
        while len(x_points) != 0:
            count = 0
            if curent_segment == 1:
                
                if count == 0: #Check if first iteration 
                    self.skip_x.clear()  #clear skip lists
                    self.skip_y.clear()  #clear skip lists                                                  
                    next_seg = 2
                    for i in range(len(x_points)):
                        j = 0
                        if next_seg == 2:
                            if quart_width < x_points[j]:
                                self.skip_x.append(x_points[j])
                                self.skip_y.append(y_points[j])
                                x_points.remove(x_points[j])
                                y_points.remove(y_points[j])
                        elif next_seg == 4:
                                self.skip_x.append(x_points[j])
                                self.skip_y.append(y_points[j])
                                x_points.remove(x_points[j])
                                y_points.remove(y_points[j])
                        j += 1
                    count += 1
                x_index = x_points.index(min(x_points))   #Find shortest x dist from origin
                y_index = y_points.index(min(y_points))   #Find shortest y dist from origin
                dist1 = x_points[x_index]**2 + y_points[x_index]**2  #Calaculate shortest dist to next x point
                dist2 = x_points[y_index]**2 + y_points[y_index]**2  #Calaculate shortest dist to next x point
                if dist2 >= dist1:
                    self.route.append(x_points[x_index])
                    self.route.append(y_points[x_index])
                    x_points.remove(x_points[x_index])
                    y_points.remove(y_points[x_index])
                else:
                    self.route.append(x_points[y_index])
                    self.route.append(y_points[y_index])
                    x_points.remove(x_points[y_index])
                    y_points.remove(y_points[y_index])
            if curent_segment == 2:
                x_index = x_points.index(min(x_points))   #Find shortest x dist from origin
                y_index = y_points.index(min(y_points))   #Find shortest y dist from origin
                dist1 = x_points[x_index]**2 + y_points[x_index]**2  #Calaculate shortest dist to next x point
                dist2 = x_points[y_index]**2 + y_points[y_index]**2  #Calaculate shortest dist to next x point
                if dist2 >= dist1:
                    self.route.append(x_points[x_index])
                    self.route.append(y_points[x_index])
                    x_points.remove(x_points[x_index])
                    y_points.remove(y_points[x_index])
                else:
                    self.route.append(x_points[y_index])
                    self.route.append(y_points[y_index])
                    x_points.remove(x_points[y_index])
                    y_points.remove(y_points[y_index])
            if curent_segment == 3:
                x_index = x_points.index(min(x_points))   #Find shortest x dist from origin
                y_index = y_points.index(max(y_points))   #Find shortest y dist from origin
                dist1 = x_points[x_index]**2 + y_points[x_index]**2  #Calaculate shortest dist to next x point
                dist2 = x_points[y_index]**2 + y_points[y_index]**2  #Calaculate shortest dist to next x point
                if dist2 >= dist1:
                    self.route.append(x_points[x_index])
                    self.route.append(y_points[x_index])
                    x_points.remove(x_points[x_index])
                    y_points.remove(y_points[x_index])
                else:
                    self.route.append(x_points[y_index])
                    self.route.append(y_points[y_index])
                    x_points.remove(x_points[y_index])
                    y_points.remove(y_points[y_index])
            if curent_segment == 4:
                x_index = x_points.index(max(x_points))   #Find shortest x dist from origin
                y_index = y_points.index(max(y_points))   #Find shortest y dist from origin
                dist1 = x_points[x_index]**2 + y_points[x_index]**2  #Calaculate shortest dist to next x point
                dist2 = x_points[y_index]**2 + y_points[y_index]**2  #Calaculate shortest dist to next x point
                if dist2 <= dist1:
                    self.route.append(x_points[x_index])
                    self.route.append(y_points[x_index])
                    x_points.remove(x_points[x_index])
                    y_points.remove(y_points[x_index])
                else:
                    self.route.append(x_points[y_index])
                    self.route.append(y_points[y_index])
                    x_points.remove(x_points[y_index])
                    y_points.remove(y_points[y_index])
        return
    
    def segment_and_solve(self, x_points, y_points):
        half_width = width/2
        half_height = height/2
        seg_1x_points = []
        seg_1y_points = []
        seg_2x_points = []
        seg_2y_points = []
        seg_3x_points = []
        seg_3y_points = []
        seg_4x_points = []
        seg_4y_points = []
        for i in range(len(x_points)):
           if(x_points[i] < half_width):
               if(y_points[i] < half_height):
                   seg_1x_points.append(x_points[i])
                   seg_1y_points.append(y_points[i])
               else:
                   seg_2x_points.append(x_points[i])
                   seg_2y_points.append(y_points[i])
           if(x_points[i] > half_width):
               if(y_points[i] < half_height):
                   seg_4x_points.append(x_points[i])
                   seg_4y_points.append(y_points[i])
               else:
                   seg_3x_points.append(x_points[i])
                   seg_3y_points.append(y_points[i])
        self.solve_segment(seg_1x_points, seg_1y_points, 1)
        self.solve_segment(seg_2x_points, seg_2y_points, 2)
        self.solve_segment(seg_3x_points, seg_3y_points, 3)
        self.solve_segment(seg_4x_points, seg_4y_points, 4)
        c = len(self.skip_x)- 1
        for i in range(len(self.skip_x)):
            self.route.append(self.skip_x[c])
            self.route.append(self.skip_y[c])
            c -= 1
            
    def on_pushButton_clicked(self):
        self.img = img3.copy()
        pixmap = QPixmap(toQImage(self.img, False))
        self.pixelmap = pixmap.scaled(self.width, self.height)        
        self.textEdit.setText('Image Loaded')
        self.label.setPixmap(self.pixelmap)
    
    def on_pushButton_2_clicked(self):
        self.img = draw_ellipses(sausages, blue, self.img)
        self.label_objects(sausages, "sausage")
        pixmap = QPixmap(toQImage(self.img, False))
        self.pixelmap = pixmap.scaled(self.width, self.height) 
        self.textEdit.setText(str(len(sausages)) + ' Sausages Located')
        self.label.setPixmap(self.pixelmap)
    
    def on_pushButton_3_clicked(self):
        self.pushButton_3.clicked.disconnect()
        self.img = draw_ellipses(corn, light_purple, self.img)
        self.label_objects(corn, "corn")
        pixmap = QPixmap(toQImage(self.img, False))
        self.pixelmap = pixmap.scaled(self.width, self.height) 
        self.textEdit.append(str(len(corn)) + ' Corn Located')
        self.label.setPixmap(self.pixelmap)
        self.pushButton_3.clicked.connect(self.on_pushButton_3_clicked)

    def on_pushButton_4_clicked(self):
        self.pushButton_4.clicked.disconnect()
        self.img = draw_ellipses(onion, purple, self.img)
        self.label_objects(onion, "onion")
        pixmap = QPixmap(toQImage(self.img, False))
        self.pixelmap = pixmap.scaled(self.width, self.height) 
        self.textEdit.append(str(len(onion)) + ' Onion Located')
        self.label.setPixmap(self.pixelmap)
        self.pushButton_4.clicked.connect(self.on_pushButton_4_clicked)
        
    def on_pushButton_5_clicked(self):
        self.pushButton_5.clicked.disconnect()
        self.route.clear()
        self.find_centres(self.objects)
        self.textEdit.append('Optimal Route Found')
        for i in range(len(self.x_c)):
            self.textEdit.append(str(i+1)+": ( "+ str(self.x_c[i]) + " , " + str(self.y_c[i]) + " )")
        self.segment_and_solve(self.x_c, self.y_c)
        self.img = draw_lines(self.route, black, self.img)
        pixmap = QPixmap(toQImage(self.img, False))
        self.pixelmap = pixmap.scaled(self.width, self.height) 
        self.label.setPixmap(self.pixelmap)
        self.pushButton_5.clicked.connect(self.on_pushButton_5_clicked)
        self.root_dist = self.find_route_length(self.route)
        self.textEdit.append('Route Length = ' + str(int(self.root_dist)) + ' px')
        
    def on_pushButton_6_clicked(self):
        img4 = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
        cv2.imwrite("modified.jpg", img4)
        self.textEdit.setText('Modified Image Saved')
    
    def find_centres(self, objects):
            self.x_c.clear()
            self.y_c.clear()
            moments = objects[0]
            for i in range(len(objects)):
                moments = cv2.moments(objects[i])
                self.x_c.append(int(moments['m10']/moments['m00']))
                self.y_c.append(int(moments['m01']/moments['m00']))
                
    def label_objects(self, objects, label): 
        self.find_centres(objects)
        for i in range(len(self.x_c)):
            if self.y_c[i]-(self.y_c[i-1]) < 10:
                offset = 50
            else:
                offset = -50
            cv2.putText(self.img, label + " at x" + str(round(self.x_c[i])) + ",y" + str(round(self.y_c[i])), (self.x_c[i]-100,self.y_c[i]+offset),cv2.FONT_HERSHEY_SIMPLEX, 1, red, 3)

    

app = QApplication(sys.argv)
widget = ObjectDetection()
widget.show()
sys.exit(app.exec_())

      
