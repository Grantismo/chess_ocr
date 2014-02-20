import cv2
import numpy as np

def detect_CheSS_corner(img):
  h, w = img.shape
  response = np.empty(w * h, dtype=np.uint16)
  image = img.reshape(w * h)
  print img.shape
  print image.shape

  for y in xrange(7, h - 7):
    for x in xrange(7, w - 7):
      offset = x + y * w
      circular_sample = np.empty(16, dtype=np.uint8)

      circular_sample[2] = image[offset - 2 - 5 * w]
      circular_sample[1] = image[offset - 5 * w]
      circular_sample[0] = image[offset + 2 - 5 * w]
      circular_sample[8] = image[offset - 2 + 5 * w]
      circular_sample[9] = image[offset + 5 * w]
      circular_sample[10] = image[offset + 2 + 5 * w]
      circular_sample[3] = image[offset - 4 - 4 * w]
      circular_sample[15] = image[offset + 4 - 4 * w]
      circular_sample[7] = image[offset - 4 + 4 * w]
      circular_sample[11] = image[offset + 4 + 4 * w]
      circular_sample[4] = image[offset - 5 - 2 * w]
      circular_sample[14] = image[offset + 5 - 2 * w]
      circular_sample[6] = image[offset - 5 + 2 * w]
      circular_sample[12] = image[offset + 5 + 2 * w]
      circular_sample[5] = image[offset - 5]
      circular_sample[13] = image[offset + 5]
      
      # purely horizontal local_mean samples
      local_mean = (int(image[offset - 1]) + int(image[offset]) + int(image[offset + 1])) * 16 / 3
      
      sum_response = 0
      diff_response = 0
      mean = 0
      
      for sub_idx in xrange(0, 4):
        a = circular_sample[sub_idx]
        b = circular_sample[sub_idx + 4]
        c = circular_sample[sub_idx + 8]
        d = circular_sample[sub_idx + 12]

        sum_response += abs(int(a) - int(b) + int(c) - int(d))
        diff_response += abs(int(a) - int(c)) + abs(int(b) - int(d))
        mean += int(a) + int(b) + int(c) + int(d)

      response[offset] = int(sum_response) - int(diff_response) - abs(int(mean) - int(local_mean))
  print response.shape

  response = response.reshape(h, w)
  cv2.convertScaleAbs(response)
  return response


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

