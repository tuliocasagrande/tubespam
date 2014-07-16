import os
import numpy
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn import naive_bayes, cross_validation
from sklearn.semi_supervised import LabelSpreading
#from sklearn import metrics
#from sklearn.metrics import classification_report

# It also works to check if this video has already been classified
def getClassifier(video_id):
  try:
    return joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))
  except:
    return None

# comments = QuerySet( [Comment(id, content, tag) ])
# untaggedComments = [Comment(id, content)]
# if len(comments) >= 100, untaggedComments = []
def train(video_id, comments, untaggedComments):

  if not os.path.exists(os.path.join('app', 'classification_files')):
    os.makedirs(os.path.join('app', 'classification_files'))

  contents = []
  classes = []
  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  untaggedContents = []
  untaggedClasses = []
  for c in untaggedComments:
    untaggedContents.append(c.content)
    untaggedClasses.append(-1)

  vectorizer = CountVectorizer(min_df=1)
  X = vectorizer.fit_transform(contents + untaggedContents)
  y = numpy.asarray(classes + untaggedClasses)

  # if len(comments) < 100, it will perform semi-supervised learning
  if untaggedContents != []:
    # Semi-supervised learning with merged untagged and tagged comments
    clf, scores = semiSupervised(X, y)

    # Predicting classes of untagged commments and building a new y
    untagged_X = vectorizer.transform(untaggedContents)
    semiSupervised_y = clf.predict(untagged_X)
    y = numpy.concatenate([numpy.asarray(classes), semiSupervised_y])

  # Fiting the classifier with real and predicted classes
  # clf, scores = naiveBayes(X, y) # Multinomial NaiveBayes
  clf, scores = svmLinear(X, y) # LinearSVM
  # clf, scores = svm(X, y)     # SVM

  # Saving vectorizer & classifier
  joblib.dump(vectorizer, os.path.join('app', 'classification_files', video_id+'_vct'))
  joblib.dump(clf, os.path.join('app', 'classification_files', video_id+'_clf'))

  # Returning scores
  # x +/- 2sigma (approximately a 95% confidence interval)
  return scores.mean()*100, scores.std()*2


# untaggedComments = [Comment(id, content)]
def predict(video_id, untaggedComments):

  # Loading vectorizer & classifier
  vectorizer = joblib.load(os.path.join('app', 'classification_files', video_id+'_vct'))
  clf = joblib.load(os.path.join('app', 'classification_files', video_id+'_clf'))

  contents = []
  for c in untaggedComments:
    contents.append(c.content)

  X = vectorizer.transform(contents)
  p = clf.predict(X)

  return p

def naiveBayes(X, y):
  clf = naive_bayes.MultinomialNB(alpha=.01)
  scores = cross_validation.cross_val_score(clf, X, y, cv=10)
  return clf, scores

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

def semiSupervised(X, y):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = {'gamma': range5}

  # It will:
  # 1- Perform the GridSearch;
  # 2- Cross-validate with 10 folds
  # 3- Generate an instance of the trained classifier (best_estimator_)
  grid = GridSearchCV(LabelSpreading(kernel='rbf'), param_grid, cv=10)
  grid.fit(X, y)

  # Only parameters passed in param_grid (and therefore evaluated as the best)
  best_parameters = grid.best_params_

  # Array with accuracies achieved by cross-validation
  for params, mean_score, scores in grid.grid_scores_:
    if params == best_parameters:
      best_scores = scores

  # Returning instance of the classifier and accuracies
  return grid.best_estimator_, best_scores
