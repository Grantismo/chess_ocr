#! /usr/bin/env python
import cv2
import numpy as np

def show_image(img, wait=False):
  WINDOW_NAME = "board"
  screen_res = 1280, 720
  scale_width = screen_res[0] / img.shape[1]
  scale_height = screen_res[1] / img.shape[0]
  scale = min(scale_width, scale_height)
  window_width = int(img.shape[1] * scale)
  window_height = int(img.shape[0] * scale)
  cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(WINDOW_NAME, window_width, window_height)
  
  cv2.imshow(WINDOW_NAME, img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def biggest_square(img):
  contours, hierarchy = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  biggest = None
  max_area = 0
  
  for i in contours:
    area = cv2.contourArea(i)
    peri = cv2.arcLength(i,True)
    approx = cv2.approxPolyDP(i, 0.02 * peri, True)
    if area > max_area and len(approx) == 4:
      max_area = area
      biggest = approx
  return biggest

def detect_edges(img, min_length, direction="x", ):
  scale = 1
  delta = 0
  ddepth = cv2.CV_16S

  if direction == "x":
    x_mult = 1
    y_mult = 0
  else:
    x_mult = 0
    y_mult = 1

  d = cv2.Sobel(img, ddepth, 1*y_mult , 1*x_mult, ksize = 3, scale = scale, delta = delta, borderType = cv2.BORDER_DEFAULT)
  d = cv2.convertScaleAbs(d)

  _,close = cv2.threshold(d ,0, 255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

  close = cv2.morphologyEx(close,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (10*x_mult + 1*y_mult, 10*y_mult + 1*x_mult)),iterations = 1)
  
  contour, _ = cv2.findContours(close,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  mask = np.zeros((gray.shape), np.uint8)
  for cnt in contour:
    x,y,w,h = cv2.boundingRect(cnt)
    if (direction == "x" and w > min_length) or h > min_length:
        cv2.drawContours(mask, [cnt], 0, 255, -1)
    else:
        cv2.drawContours(mask, [cnt], 0, 0, -1)
  return mask


img = cv2.imread('images/boards/board1.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
mask = np.zeros((gray.shape), np.uint8)
#show_image(thresh)


biggest = biggest_square(thresh)
x, y, width, height = cv2.boundingRect(biggest)
min_width = width * 0.75
min_height = height * 0.75

print biggest.dtype
cv2.drawContours(image=mask, contours=[biggest], contourIdx=-1, thickness=-1, color=(255, 255, 255), lineType=4, maxLevel=1)

#masked_img  = cv2.bitwise_and(gray, mask)
#thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
masked_img = cv2.bitwise_and(thresh, mask)

x_edges = detect_edges(masked_img, min_width,"x")
y_edges = detect_edges(masked_img, min_height, "y")

#show_image(x_edges)
#show_image(y_edges)

centers = cv2.bitwise_and(x_edges, y_edges) 
centers = cv2.morphologyEx(centers,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)
centers = cv2.morphologyEx(centers,cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20)),iterations = 1)


contour, hier = cv2.findContours(centers.copy(), cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

centroids = []
for cnt in contour:
  mom = cv2.moments(cnt)
  (x,y) = int(mom['m10']/mom['m00']), int(mom['m01']/mom['m00'])
#  cv2.circle(img,(x,y),4,(0,255,0),-1)
  centroids.append((x,y))


#for i, (x, y) in enumerate(centroids):
#  cv2.putText(img, str(i), (x, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255))

dtype = [('x', np.int32), ('y', np.int32)]
centroids = np.array(centroids, dtype=dtype)
centroids.sort(order="x")
centroids = centroids.reshape((9, 9, ))
for row in centroids:
  row.sort(order="y")

print centroids


squares = []
for i, row in enumerate(centroids[:-1]):
  for j, _ in enumerate(row[:-1]):
    square = []
    for x, y in [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]:
      point = centroids[x][y].tolist() #ugly hack to strip type information
      square.append(point)
    squares.append(np.array(square))

for square in squares:
  mask = np.zeros((gray.shape), np.uint8)
  cv2.drawContours(mask,[square], 0, 255, -1)

  mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
  show_image(cv2.bitwise_and(img, mask))



