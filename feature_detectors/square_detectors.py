from edge_detectors import *
from board_detectors import *
import cv2
import numpy as np
from drawing_utils import *


def detect_sobel_squares(img):
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
  show_image(gray)

  mask, x, y, width, height = get_board_mask(thresh)
  min_width = width * 0.75
  min_height = height * 0.75

  board = cv2.bitwise_and(gray, mask)
  show_image(board)

  x_edges = detect_sobel_edges(board, min_width,"x")
  y_edges = detect_sobel_edges(board, min_height, "y")
  show_image(x_edges)
  show_image(y_edges)
  
  
  centers = cv2.bitwise_and(x_edges, y_edges) 
  centers = cv2.morphologyEx(centers,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)
  centers = cv2.morphologyEx(centers,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)
  contour, hier = cv2.findContours(centers.copy(), cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
  
  centroids = []
  for cnt in contour:
    mom = cv2.moments(cnt)
    (x,y) = int(mom['m10']/mom['m00']), int(mom['m01']/mom['m00'])
    cv2.circle(img,(x,y),4,(0,255,0),-1)
    centroids.append((x,y))

  #for i, (x, y) in enumerate(centroids):
  #  cv2.putText(img, str(i), (x, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255))
  
  dtype = [('x', np.int32), ('y', np.int32)]
  centroids = np.array(centroids, dtype=dtype)
  centroids.sort(order="x")
  centroids = centroids.reshape((9, 9, ))
  for row in centroids:
    row.sort(order="y")
  
  squares = []
  for i, row in enumerate(centroids[:-1]):
    for j, _ in enumerate(row[:-1]):
      square = []
      for x, y in [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]:
        point = centroids[x][y].tolist() #ugly hack to strip type information
        square.append(point)
      squares.append(np.array(square))
  return squares
  

def detect_hough_squares(img):
  edges = detect_canny_edges(img)
  lines = cv2.HoughLines(edges,1, np.pi/180,100)
  edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
  for rho,theta in lines[0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))
    cv2.line(edges,(x1,y1),(x2,y2),(0,0,255),2)

def filter(img):
  img = cv2.GaussianBlur(img,(5,5),0)
  img = cv2.morphologyEx(img,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6)),iterations = 1)
  img = cv2.morphologyEx(img,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6)),iterations = 1)
  return img

def grayscale(img):
  img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 3, 1) 
  return img

