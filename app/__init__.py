import os
from classification import CLASSIFICATION_FILES_DIR

if not os.path.exists(CLASSIFICATION_FILES_DIR):
  os.makedirs(CLASSIFICATION_FILES_DIR)
  print "Creating new classification files directory (IT'S EMPTY!)"
