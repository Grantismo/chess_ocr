#! /usr/bin/env python
import cv2
import numpy as np
from feature_detectors import *
from drawing_utils import *

def main():
  images = [cv2.imread("images/boards/" + img) for img in ['board1.png', 'board2.jpg', 'board3.png']]
  for image in images:
    #squares = detect_sobel_squares(image.copy())
    squares = detect_hough_squares(image.copy())
    if not squares:
      print "Couldn't find board"
    #show_masked_squares(image, squares)
    highlight_squares(image, squares)
    show_image(image)


if __name__ == "__main__":
  main()
