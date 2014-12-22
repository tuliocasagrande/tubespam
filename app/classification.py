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

# comments = QuerySet( [Comment(id, author, date, content, tag) ])
# unlabeled_comments = [Comment(id, author, date, content)]
# if len(comments) >= 100, unlabeled_comments = []
def fit(video_id, comments, unlabeled_comments):

  if not os.path.exists(os.path.join('app', 'classification_files')):
    os.makedirs(os.path.join('app', 'classification_files'))

  contents = []
  classes = []
  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  unlabeled_classes = np.repeat(-1, len(unlabeled_comments))
  unlabeled_contents = [c.content for c in unlabeled_comments]

  vectorizer = CountVectorizer(min_df=1)
  X = vectorizer.fit_transform(contents + unlabeled_contents)
  y = np.concatenate([classes, unlabeled_classes])

  range5 = [10.0**i for i in range(-5,5)]

  # ================= Intermediate semi-supervised classifier ================ #
  # if len(comments) < 100, it will perform semi-supervised learning

  if unlabeled_contents != []:

    # Semi-supervised learning with merged unlabeled and tagged comments
    param_grid = {'gamma': range5}
    ss_grid = GridSearchCV(LabelSpreading(kernel='rbf'), param_grid, cv=10).fit(X, y)

    # Predicting classes of unlabeled comments and building a new y
    unlabeled_X = vectorizer.transform(unlabeled_contents)
    ss_y = ss_grid.predict(unlabeled_X)
    y = np.concatenate([classes, ss_y])

  # ============================ Final classifier ============================ #
  # Fitting the classifier with manually classified and predicted comments

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
  """ Load the classifier of the video_id and predict its unlabeled_comments.
      unlabeled_comments = [Comment(id, author, date, content)]
  """

  vectorizer = joblib.load(os.path.join('app', 'classification_files', video_id+'_vct'))
  clf = joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))

  contents = [c.content for c in unlabeled_comments]
  X = vectorizer.transform(contents)
  return clf.predict(X)
