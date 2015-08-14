import numpy as np
import os
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
# from sklearn.metrics import make_scorer, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

CLASSIFICATION_FILES_DIR = 'tubespam_classification_files'

def has_classifier(video_id):
  """ Return true if the given video_id has a stored classifier.
  """
  try:
    joblib.load(os.path.join(CLASSIFICATION_FILES_DIR, video_id+'_grid'))
    return True
  except:
    return False


def fit(video_id, comments):
  """ Supervised training with LinearSVM
      comments = QuerySet( [Comment(id, author, date, content, tag)] )
  """

  if not os.path.exists(CLASSIFICATION_FILES_DIR):
    os.makedirs(CLASSIFICATION_FILES_DIR)

  X = []
  y = []
  for c in comments:
    X.append(c.content)
    y.append(1 if c.tag else 0)

  pipeline = Pipeline([('vectorizer', CountVectorizer()),
                       ('svm', LinearSVC())])

  # mcc = make_scorer(matthews_corrcoef)
  parameters = {'svm__C': [10.0**i for i in range(-5,5)]}
  grid = GridSearchCV(pipeline, parameters, cv=10)
  grid.fit(X, y)

  # Saving the entire grid & pipeline
  joblib.dump(grid, os.path.join(CLASSIFICATION_FILES_DIR, video_id+'_grid'))

  # Array with accuracies achieved by cross-validation
  for parameters, mean_validation_score, cv_validation_scores in grid.grid_scores_:
    if parameters == grid.best_params_:

      # Returning scores
      # mean +/- 2sigma (approximately a 95% confidence interval)
      return grid.best_params_['svm__C'], cv_validation_scores.mean()*100, cv_validation_scores.std()*2


def predict(video_id, unlabeled_comments):
  """ Load the classifier of the given video_id and predict its unlabeled_comments.
      unlabeled_comments = [Comment(id, author, date, content)]
  """

  grid = joblib.load(os.path.join(CLASSIFICATION_FILES_DIR, video_id+'_grid'))

  if unlabeled_comments and type(unlabeled_comments[0]) == dict:
    X = [c['content'] for c in unlabeled_comments]
  else:
    X = [c.content for c in unlabeled_comments]

  return grid.predict(X)
