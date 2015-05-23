import numpy as np
import os
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.semi_supervised import LabelSpreading
from sklearn.svm import LinearSVC

def get_classifier(video_id):
  """ Return the stored classifier of the given video_id.
      Return None if the video has yet to be classified.
  """
  try:
    return joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))
  except:
    return None

def fit(video_id, comments, unlabeled_comments):
  """ Dual supervised training
      Training/fitting occurs in two steps:

      1- Fit the LabelSpreading semi-supervised method with RBF kernel. It is
      much faster than SVM and can be pretty accurate.

      2- Classify unlabeled comments and retain the labels with a high level of
      certainty to be used in the SVM fitting.

      comments = QuerySet( [Comment(id, author, date, content, tag)] )
      unlabeled_comments = [Comment(id, author, date, content)]
  """

  if not os.path.exists(os.path.join('app', 'classification_files')):
    os.makedirs(os.path.join('app', 'classification_files'))

  # Semi-supervised will at most double the training set
  unlabeled_comments = unlabeled_comments[: len(comments)]

  contents = []
  classes = []
  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  unlabeled_classes = np.repeat(-1, len(unlabeled_comments))
  unlabeled_contents = np.asarray([c.content for c in unlabeled_comments])

  vectorizer = CountVectorizer(min_df=1)
  X = vectorizer.fit_transform(np.concatenate([contents, unlabeled_contents]))
  y = np.concatenate([classes, unlabeled_classes])

  range5 = [10.0**i for i in range(-5,5)]

  # ================= Intermediate semi-supervised classifier ================ #
  # Semi-supervised clf with merged manually classified and unlabeled comments

  param_grid = {'gamma': range5}
  ss_grid = GridSearchCV(LabelSpreading(kernel='rbf'), param_grid, cv=10).fit(X.toarray(), y)

  # Predicting classes and probabilities of unlabeled comments
  unlabeled_X = vectorizer.transform(unlabeled_contents)
  ss_pred = ss_grid.predict(unlabeled_X)
  ss_proba = ss_grid.predict_proba(unlabeled_X)

  # Building a new y just with comments above 0.9 of probability
  above_threshold = [each[ss_pred[i]] >= 0.9 for i, each in enumerate(ss_proba)]
  above_threshold = np.asarray(above_threshold)

  vectorizer = CountVectorizer(min_df=1)
  X = vectorizer.fit_transform(np.concatenate([contents, unlabeled_contents[above_threshold]]))
  y = np.concatenate([classes, ss_pred[above_threshold]])

  # ============================ Final classifier ============================ #
  # Fitting the final clf with manually classified and predicted comments

  param_grid = {'C': range5}
  svm_grid = GridSearchCV(LinearSVC(), param_grid, cv=10).fit(X, y)

  # Saving vectorizer & classifier
  joblib.dump(vectorizer, os.path.join('app', 'classification_files', video_id+'_vct'))
  joblib.dump(svm_grid.best_estimator_, os.path.join('app', 'classification_files', video_id+'_clf'))

  # Array with accuracies achieved by cross-validation
  for parameters, mean_validation_score, cv_validation_scores in svm_grid.grid_scores_:
    if parameters == svm_grid.best_params_:

      # Returning scores
      # mean +/- 2sigma (approximately a 95% confidence interval)
      return cv_validation_scores.mean()*100, cv_validation_scores.std()*2


def predict(video_id, unlabeled_comments):
  """ Load the classifier of the given video_id and predict its unlabeled_comments.
      unlabeled_comments = [Comment(id, author, date, content)]
  """

  vectorizer = joblib.load(os.path.join('app', 'classification_files', video_id+'_vct'))
  clf = joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))

  if unlabeled_comments and type(unlabeled_comments[0]) == dict:
    contents = [c['content'] for c in unlabeled_comments]
  else:
    contents = [c.content for c in unlabeled_comments]

  X = vectorizer.transform(contents)
  return clf.predict(X)
