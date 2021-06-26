import cv2
import numpy as np
import math
import RPi.GPIO as GPIO
from time import sleep
import time
import car
import matplotlib.pyplot as plt

car.car_setup()
#car.car_stop()
 
def convert_to_HSV(frame):
  #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Convert to Grayscale
  cv2.GaussianBlur(hsv,(5,5),0)
  cv2.imshow("HSV",hsv)
  #print(time.time())
  return hsv

def detect_edges(frame):
    #lower_blue = np.array([200, 200,200 ], dtype = "uint8") # lower limit of blue color
    #upper_blue = np.array([250, 255, 255], dtype="uint8") # upper limit of blue color
    mask = cv2.inRange(hsv,180,255) # this mask will filter out everything but blue

    # detect edges
    edges = cv2.Canny(mask,100,100) 
    cv2.imshow("edges",edges)
    return edges

def region_of_interest(edges):
    height, width = edges.shape # extract the height and width of the edges frame
    mask = np.zeros_like(edges) # make an empty matrix with same dimensions of the edges frame

    # only focus lower half of the screen
    # specify the coordinates of 4 points (lower left, upper left, upper right, lower right)
    polygon = np.array([[
        (0, height), 
        (0,  height/2),
        (width , height/2),
        (width , height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255) # fill the polygon with blue color 
    cropped_edges = cv2.bitwise_and(edges, mask) 
    cv2.imshow("roi",cropped_edges)
    return cropped_edges

def detect_line_segments(cropped_edges):
    rho = 1  
    theta = np.pi / 180  
    min_threshold = 20  #10 original value
    line_segments = cv2.HoughLinesP(cropped_edges, rho, theta, min_threshold, 
                                    np.array([]), minLineLength=5, maxLineGap=0)
    #cv2.imshow("line segments",line_segments)
    plt.plot()
    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []

    if line_segments is None:
        print("no line segment detected")
        return lane_lines

    height, width,_ = frame.shape
    left_fit = []
    right_fit = []
    boundary = 1/3

    left_region_boundary = width * (1 - boundary) 
    right_region_boundary = width * boundary 

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                #print("skipping vertical lines (slope = infinity)")
                continue

            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - (slope * x1)

            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
                    #print("Test1")
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))
                    #print("Test2")
                    
    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))
        #print("Test3")
    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))
        #print("Test4")
    # lane_lines is a 2-D array consisting the coordinates of the right and left lane lines
    # for example: lane_lines = [[x1,y1,x2,y2],[x1,y1,x2,y2]]
    # where the left array is for left lane and the right array is for right lane 
    # all coordinate points are in pixels
    
    return lane_lines

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 / 2)  # make points from middle of the frame down

    if slope == 0: 
        slope = 0.1    

    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return [[x1, y1, x2, y2]]

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=6): # line color (B,G,R)
    line_image = np.zeros_like(frame)

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)

    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)  
    return line_image

#output = alpha * image1 + beta * image2 + gamma

def get_steering_angle(frame, lane_lines):
    height, width, _ = frame.shape

    if len(lane_lines) == 2: # if two lane lines are detected
        _, _, left_x2, _ = lane_lines[0][0] # extract left x2 from lane_lines array
        _, _, right_x2, _ = lane_lines[1][0] # extract right x2 from lane_lines array
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
            
     
    elif len(lane_lines) == 1: # if only one line is detected
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)

    elif len(lane_lines) == 0: # if no line is detected
        x_offset = 0
        y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  
    steering_angle = angle_to_mid_deg + 90
    #print(steering_angle)
    return steering_angle
    

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):

    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)

    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
video.set(cv2.CAP_PROP_FRAME_HEIGHT,240)


#speed = 10

        
#Variables to be updated each loop
lastTime = 0 
lastError = 0

# PD constants
#kp = 0.4
#kd = kp * 0.65

sleeptime = 0.1
deviationThresholdMax = 5
deviationThresholdMin = -5



while True:
    #print("Inside While")
    
    #thread = threading.Thread(target=frames)
    #thread.start()
    ret,frame = video.read()    
    frame = cv2.flip(frame,-1)

  
    #Calling the functions
    hsv = convert_to_HSV(frame)
    edges = detect_edges(hsv)
    roi = region_of_interest(edges)
    line_segments = detect_line_segments(roi)
    #lane_lines = average_slope_intercept(frame,line_segments)
    #lane_lines_image = display_lines(frame,lane_lines)
    #steering_angle = get_steering_angle(frame, lane_lines)
    #sleep(4)
    
    #now = time.time() # current time variable
    #dt = now - lastTime
    #deviation = steering_angle - 90 # equivalent to angle_to_mid_deg variable
    #error = abs(deviation) 

    #print(deviation)
    
    #if deviation < deviationThresholdMax and deviation > deviationThresholdMin: # do not steer if there is a 10-degree error range
        #deviation = 0
        #error = 0
        #car.car_stop()
        #car.car_forward(sleeptime)
        #print("A")
        
    #elif deviation > deviationThresholdMax: # steer right if the deviation is positive
        #car.car_stop()
        #car.car_pivotright(sleeptime)
        #print("B")
    #elif deviation < deviationThresholdMin: # steer left if deviation is negative
        #car.car_stop()
        #car.car_forward(sleeptime)
        #car.car_pivotleft(sleeptime)
        #print("C")
        
    #derivative = kd * (error - lastError) / dt 
    #proportional = kp * error
    #PD = int(speed + derivative + proportional)

    #spd = abs(PD)
    #if spd > 25:
       #spd = 25

    #throttle.start(spd)

    #lastError = error
    #lastTime = time.time()
    
    #car.car_reset()
    #car.car_stop(1)
    
    #plt.plot(line_segments)
    
    key = cv2.waitKey(1)
    if key == 27:
        break
    
    #sleep(4)
#sleep(4)
print(line_segments)
#print(lane_lines)
#print(lane_lines)
print(line_segments.shape)

video.release()
cv2.destroyAllWindows()
