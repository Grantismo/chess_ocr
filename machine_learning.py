import cv2
import numpy as np
import glob
from drawing_utils import *

def knn():

  total_samples = len(glob.glob("images/training_data/**/*"))
  feature_dim = (30, 30)
  feature_length = feature_dim[0] * feature_dim[1]

  samples = np.zeros((total_samples, feature_length), dtype=np.float32)
  responses = []

  training_folders = glob.glob("images/training_data/*")
  i = 0
  for f in training_folders: 
    piece_type = f[21:]  
    for training_image in glob.glob(f + "/*"):
      img = cv2.imread(training_image)
      gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
      train = cv2.resize(gray, feature_dim)

      train = train.reshape(1, feature_length)
      samples[i] = train
      i += 1
      responses.append(ord(piece_type))
  responses = np.array(responses, dtype=np.float32)
  responses = responses.reshape((responses.size, 1))

  test_samples = samples[-10:]
  test_responses = responses[-10:]

  samples = samples[:-10]
  responses = responses[:-10]


  knn = cv2.KNearest()
  knn.train(samples, responses)
  ret, result, neighbours, dist = knn.find_nearest(test_samples, k=1)

  matches = result == test_responses
  correct = np.count_nonzero(matches)

  accuracy = correct*100.0 / result.size
  print accuracy
