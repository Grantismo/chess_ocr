import cv2
import numpy as np

def show_image(img):
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

def show_masked_squares(img, squares):
  for square in squares:
    mask = np.zeros((img.shape), np.uint8)
    cv2.drawContours(mask,[square], 0, (255, 255, 255), -1)

    #mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    show_image(cv2.bitwise_and(img, mask))

def highlight_squares(img, squares):
  for square in squares:
    cv2.drawContours(img, [square], 0, (0, 0, 255), 2)
    
