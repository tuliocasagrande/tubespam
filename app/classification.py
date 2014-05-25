import os
import numpy
# import pickle
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn import cross_validation
from sklearn import naive_bayes, svm, linear_model
from sklearn.semi_supervised import LabelSpreading
from sklearn.semi_supervised import LabelPropagation
#from sklearn import metrics
#from sklearn.metrics import classification_report


def classify(comments):
  contents = []
  classes = []

  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  classes = numpy.asarray(classes)
  vectorizer = CountVectorizer(min_df=1)
  bagOfWords = vectorizer.fit_transform(contents)

  if not os.path.exists(os.path.join('app', 'classification_models')):
    os.makedirs(os.path.join('app', 'classification_models'))

  # CLASSIFIERS ======================================

  output = "Multinomial NB:\n" + naiveBayes(bagOfWords, classes)
  output += "\n\nLogistic Regression: " + logistic(bagOfWords, classes)
  output += "\n\nSVMLinear: " + svmLinear(bagOfWords, classes)
  output += "\n\nSVM: " + svmGS(bagOfWords, classes)

  output += '\n\n\n(saving SVM to disk) ... (loading model SVM disk)\n\n'

  p = svmLoaded(bagOfWords)
  output += '\n\nComment | Prediction | Class\n'
  for i in range(len(comments)):
    output += '%s | %d | %d\n' % (comments[i].content, p[i], classes[i])

  return output

def acc(scores):
  return "Accuracy: %0.2f%% (+/- %0.3f)" % (scores.mean() * 100, scores.std() * 2)

def naiveBayes(bow, classes):
  clf = naive_bayes.MultinomialNB(alpha=.01)
  scores = cross_validation.cross_val_score(clf, bow, classes, cv=10)

  output = acc(scores)
  return output


def logistic(bow, classes):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = [{'C': range5}]
  grid = GridSearchCV(linear_model.LogisticRegression(), param_grid, cv=10).fit(bow, classes)

  clf = linear_model.LogisticRegression(C=grid.best_estimator_.C)
  scores = cross_validation.cross_val_score(clf, bow, classes, cv=10)

  output = '\n--> Melhores parametros:\n'
  output += '\tC: %f\n' % (grid.best_estimator_.C)
  output += acc(scores)
  return output

def svmLinear(bow, classes):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = [{'C': range5}]
  grid = GridSearchCV(svm.LinearSVC(), param_grid, cv=10).fit(bow, classes)

  clf = svm.LinearSVC(C=grid.best_estimator_.C)
  scores = cross_validation.cross_val_score(clf, bow, classes, cv=10)

  output = '\n--> Melhores parametros:\n'
  output += '\tC: %f\n' % (grid.best_estimator_.C)
  output += acc(scores)
  return output

def svmGS(bow, classes):
  range5 = list((10.0**i) for i in range(-5,5))
  param_grid = [
    {'C': range5, 'kernel': ['linear']},
    {'C': range5, 'gamma': range5, 'kernel': ['rbf']},
    {'C': range5, 'gamma': range5, 'kernel': ['poly']},
  ]
  grid = GridSearchCV(svm.SVC(), param_grid, cv=10).fit(bow, classes)

  clf = svm.SVC(kernel=grid.best_estimator_.kernel,
        C=grid.best_estimator_.C,
        gamma=grid.best_estimator_.gamma)
  scores = cross_validation.cross_val_score(clf, bow, classes, cv=10)

  joblib.dump(clf.fit(bow, classes), os.path.join('app', 'classification_models', 'filename.pkl'))

  output = '\n--> Melhores parametros:\n'
  output += '\tKernel: %s\n' % (grid.best_estimator_.kernel)
  output += '\tC: %f\n' % (grid.best_estimator_.C)
  if (grid.best_estimator_.kernel != 'linear'):
    output += '\tGamma: %f\n' % (grid.best_estimator_.gamma)
  output += acc(scores)
  return output


def svmLoaded(bow):
  clf = joblib.load(os.path.join('app', 'classification_models', 'filename.pkl'))
  return clf.predict(bow)
