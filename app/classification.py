import os
import numpy
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn.semi_supervised import LabelSpreading
from sklearn.semi_supervised import LabelPropagation
#from sklearn import metrics
#from sklearn.metrics import classification_report

def getClassifier(video_id):
  try:
    return joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))
  except:
    return None

# comments = QuerySet( [Comment(id, content, tag) ])
def train(video_id, comments):

  if not os.path.exists(os.path.join('app', 'classification_files')):
    os.makedirs(os.path.join('app', 'classification_files'))

  contents = []
  classes = []

  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  vectorizer = CountVectorizer(min_df=1)
  X = vectorizer.fit_transform(contents)
  y = numpy.asarray(classes)

  # LinearSVM
  clf, scores = svmLinear(X, y)
  #print clf.get_params()['C']

  # SVM
  # clf, scores = svm(X, y)

  print 'TRAIN:'
  print 'Comment - Prediction - Label'
  p = clf.predict(X)
  for i in range(len(contents)):
    print '%s - %d - %d' % (contents[i], p[i], y[i])

  # Saving vectorizer & classifier
  joblib.dump(vectorizer, os.path.join('app', 'classification_files', video_id+'_vct'))
  joblib.dump(clf, os.path.join('app', 'classification_files', video_id+'_clf'))

  # Returning scores
  # x +/- 2sigma (approximately a 95% confidence interval)
  return scores.mean()*100, scores.std()*2

# untagged_contents = [content, ...]
def predict(video_id, untagged_contents):

  # Loading vectorizer & classifier
  vectorizer = joblib.load(os.path.join('app', 'classification_files', video_id+'_vct'))
  clf = joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))

  X = vectorizer.transform(untagged_contents)

  print 'PREDICTION:'
  print 'Comment - Prediction'
  p = clf.predict(X)
  for i in range(len(untagged_contents)):
    print '%s - %d' % (untagged_contents[i], p[i])

  return p

def svmLinear(X, y):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = {'C': range5}

  # It will:
  # 1- Perform the GridSearch;
  # 2- Cross-validate with 10 folds
  # 3- Generate an instance of the trained classifier (best_estimator_)
  grid = GridSearchCV(LinearSVC(), param_grid, cv=10)
  grid.fit(X, y)

  # Only parameters passed in param_grid (and therefore evaluated as the best)
  best_parameters = grid.best_params_

  # Array with accuracies achieved by cross-validation
  for params, mean_score, scores in grid.grid_scores_:
    if params == best_parameters:
      best_scores = scores

  # Returning instance of the classifier and accuracies
  return grid.best_estimator_, best_scores

def svm(X, y):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = [
    {'kernel': ['linear'], 'C': range5},
    {'kernel': ['rbf'], 'C': range5, 'gamma': range5},
    {'kernel': ['poly'], 'C': range5, 'gamma': range5},
  ]

  # It will:
  # 1- Perform the GridSearch;
  # 2- Cross-validate with 10 folds
  # 3- Generate an instance of the trained classifier (best_estimator_)
  grid = GridSearchCV(SVC(), param_grid, cv=10)
  grid.fit(X, y)

  # Only parameters passed in param_grid (and therefore evaluated as the best)
  best_parameters = grid.best_params_

  # Array with accuracies achieved by cross-validation
  for params, mean_score, scores in grid.grid_scores_:
    if params == best_parameters:
      best_scores = scores

  # Returning instance of the classifier and accuracies
  return grid.best_estimator_, best_scores
