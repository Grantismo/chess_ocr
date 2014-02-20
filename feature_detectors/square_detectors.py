from edge_detectors import *
from board_detectors import *
import cv2
import numpy as np
from drawing_utils import *
import sys


def detect_sobel_squares(img):
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)

  mask, x, y, width, height = get_board_mask(thresh)
  min_width = width * 0.75
  min_height = height * 0.75

  board = cv2.bitwise_and(gray, mask)

  x_edges = detect_sobel_edges(board, min_width,"x")
  y_edges = detect_sobel_edges(board, min_height, "y")
  
  
  centers = cv2.bitwise_and(x_edges, y_edges) 
  return squares_from_corner_image(centers)


  
def detect_chess_corners(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray,(3,3),0)
  gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 3, 2) 

  gray = cv2.morphologyEx(gray,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)
  gray = cv2.morphologyEx(gray,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)


  mask, x, y, width, height = get_board_mask(gray)
  roi = gray[y: y+ height, x: x + width]

  corners = detect_CheSS_corner(roi)

def detect_hough_squares(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray,(3,3),0)
  gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 3, 2) 

  gray = cv2.morphologyEx(gray,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)
  gray = cv2.morphologyEx(gray,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)


  bm = get_board_mask(gray)

  if bm is False:
    return False

  mask, x, y, width, height = bm
  roi = gray[y - 10: y + height + 10, x - 10: x + width + 10]

  edges = cv2.Canny(roi, 10, 120, apertureSize = 5)

  edges = cv2.morphologyEx(edges,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),iterations = 1)

  lines = cv2.HoughLines(edges,1, np.pi/180, 180)
  edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
  
  show_image(edges)
  #roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
  v_lines = []
  h_lines = []
  for rho, theta in lines[0]:
    h = (np.pi / 2 - 0.02)  < theta and theta < (np.pi / 2 + 0.02)
    v = theta < 0.02
    if v:
      v_lines.append((rho, theta))
      
    if h: 
      h_lines.append((rho, theta))

    if h or v:
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a*rho
      y0 = b*rho
      x1 = int(x0 + 1000*(-b))
      y1 = int(y0 + 1000*(a))
      x2 = int(x0 - 1000*(-b))
      y2 = int(y0 - 1000*(a))

      cv2.line(roi,(x1,y1),(x2,y2),(0,0,100),1)

  centers = np.zeros((gray.shape), np.uint8)
  for v in v_lines:
    for h in h_lines:
       p = intersection(v, h)
       if p is not False:
         intersect = (int(x - 10 + p[0]), int(y - 10 + p[1]))
         cv2.circle(centers, intersect, 3, 255, -1)

  return squares_from_corner_image(centers)


def intersection(l1, l2):

  # A = [cos t1  sin t1]   b = |r1|   X = |x|
  #     [cos t2  sin t2]       |r2|       |y|
  # AX = b 

  r1, t1 = l1
  r2, t2 = l2
  a = np.array([[np.cos(t1), np.sin(t1)], [np.cos(t2), np.sin(t2)]])
  b = np.array([r1, r2])
  try:
    return np.linalg.solve(a, b)
  except np.linalg.LinAlgError:
    return False
    


def nothing(nodda):
  pass

def detect_harris_squares(img):
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray,(3,3),0)
  gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 3, 2) 

  gray = cv2.morphologyEx(gray,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)
  gray = cv2.morphologyEx(gray,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),iterations = 1)
  mask, x, y, width, height = get_board_mask(gray)
  roi = gray[y: y+ height, x: x + width]


  #result is dilated for marking the corners, not important
  
  # Threshold for an optimal value, it may vary depending on the image.

  dst = roi.copy()


  
  rst = cv2.cornerHarris(dst, 5, 1, 0.04)
  #dst = cv2.dilate(dst, None)
  width, height = rst.shape

  dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
  dst_max = rst.max()*0.5
  for y in xrange(0, height):
    for x in xrange(0, width):
      harris = rst[x][y]
      # check the corner detector response
      if harris > dst_max:
       # draw a small circle on the original image
       cv2.circle(dst, (x,y), 2, (255, 0, 25))


def squares_from_corner_image(centers):
  centers = cv2.morphologyEx(centers,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)
  centers = cv2.morphologyEx(centers,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)
  contour, hier = cv2.findContours(centers.copy(), cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
  
  centroids = []
  for cnt in contour:
    mom = cv2.moments(cnt)
    (x,y) = int(mom['m10']/mom['m00']), int(mom['m01']/mom['m00'])
    #cv2.circle(img,(x,y),4,(0,255,0),-1)
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


