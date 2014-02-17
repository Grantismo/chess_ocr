import cv2
import numpy as np

def get_board_mask(img):
  biggest = biggest_square(img)
  if biggest is None:
    return False

  x, y, width, height = cv2.boundingRect(biggest)

  mask = np.zeros((img.shape), np.uint8)

  cv2.drawContours(image=mask, contours=[biggest], contourIdx=-1, thickness=-1, color=(255, 255, 255), lineType=4, maxLevel=1)

  return mask, x, y, width, height

def biggest_square(img):
  contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  biggest = None
  max_area = 0

  for i in contours:
    area = cv2.contourArea(i)
    peri = cv2.arcLength(i,True)
    approx = cv2.approxPolyDP(i, 0.02 * peri, True)
    if area > max_area and len(approx) == 4:
      max_area = area
      biggest = approx

  if biggest is None:
    return False
  return biggest
