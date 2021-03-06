import numpy as np
import os
from sklearn.externals import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import BernoulliNB

CLASSIFICATION_FILES_DIR = 'tubespam_classification_files'

def _vectorize(X):
  return HashingVectorizer(binary=True, norm=None).transform(X)

def load_model(classifier):
  """ Return true if the classifier has a model saved to disk
  """
  try:
    model_path = os.path.join(CLASSIFICATION_FILES_DIR, classifier.model_filename)
    joblib.load(model_path)
    return True
  except:
    return False

def partial_fit(classifier, comments, new_fit=False):
  """ Partial fit for online/incremental learning
      comments = QuerySet( [Comment(id, author, date, content, tag)] )
  """
  if not os.path.exists(CLASSIFICATION_FILES_DIR):
    os.makedirs(CLASSIFICATION_FILES_DIR)

  model_path = os.path.join(CLASSIFICATION_FILES_DIR, classifier.model_filename)
  X = [c.content for c in comments]
  y = [int(c.tag) for c in comments]
  bag_of_words = _vectorize(X)

  if new_fit:
    model = BernoulliNB(alpha=0.001, binarize=None)
  else:
    model = joblib.load(model_path)

  model.partial_fit(bag_of_words, y, classes=[0,1])

  # Save the model
  joblib.dump(model, model_path)

def predict(classifier, unlabeled_comments):
  """ Load the classifier and predict the unlabeled_comments
      unlabeled_comments = [{'id': .. , 'author': .. , 'date': .. , 'content': .. }]
  """
  model_path = os.path.join(CLASSIFICATION_FILES_DIR, classifier.model_filename)
  X = [c['content'] for c in unlabeled_comments]
  bag_of_words = _vectorize(X)

  model = joblib.load(model_path)
  return model.predict(bag_of_words)
