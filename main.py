#! /usr/bin/env python
import cv2
import numpy as np
from feature_detectors import *
from drawing_utils import *

def main():
  images = [cv2.imread("images/boards/" + img) for img in ['board1.png']]
  for image in images:
    squares = detect_sobel_squares(image.copy())
    show_masked_squares(image, squares)


if __name__ == "__main__":
  main()
