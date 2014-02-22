#! /usr/bin/env python
import cv2
import numpy as np
from feature_detectors import *
from drawing_utils import *
from machine_learning import *
import glob
import signal


def main():
  #train()
  knn()

def train():
  files = glob.glob("images/boards/png/*")
  images = [cv2.imread(f) for f in files]

  for i, image in enumerate(images):
    if i > 4:
      print "loading ", files[i] 
      #squares = detect_sobel_squares(image.copy())
      squares = detect_hough_squares(image.copy())
      if not squares:
        print "Couldn't find board"
      write_training_data(image, squares)


if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal.SIG_DFL)
  main()
