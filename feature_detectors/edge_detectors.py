import cv2
import numpy as np

def detect_canny_edges(img):
  return cv2.Canny(img, 100, 200, apertureSize = 3)


def detect_sobel_edges(img, min_length, direction="x"):
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

  _,close = cv2.threshold(d, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

  close = cv2.morphologyEx(close,cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (10*x_mult + 1*y_mult, 10*y_mult + 1*x_mult)),iterations = 1)
  
  contour, _ = cv2.findContours(close,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  mask = np.zeros((img.shape), np.uint8)
  for cnt in contour:
    x,y,w,h = cv2.boundingRect(cnt)
    if (direction == "x" and w > min_length) or h > min_length:
        cv2.drawContours(mask, [cnt], 0, 255, -1)
    else:
        cv2.drawContours(mask, [cnt], 0, 0, -1)
  return mask

