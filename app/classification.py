import csv
import numpy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes, svm, linear_model
from sklearn import metrics
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report


def classify(comments):
  output = ''
  contents = []
  classes = []

  for c in comments:
    contents.append(c.content)
    classes.append(1 if c.tag else 0)

  classes = numpy.asarray(classes)
  vectorizer = CountVectorizer(min_df=1)
  bagOfWords = vectorizer.fit_transform(contents)

  # CLASSIFIERS ======================================

  output += "Multinomial NB: " + naiveBayes(bagOfWords, classes)
  output += "\n\nLogistic Regression: " + logistic(bagOfWords, classes)
  output += "\n\nSVMLinear: " + svmLinear(bagOfWords, classes)
  output += "\n\nSVM - Kernel Linear: " + svmKernelLinear(bagOfWords, classes)
  output += "\n\nSVM - Kernel Radial: " + svmKernelRadial(bagOfWords, classes)
  output += "\n\nSVM - Kernel Polinomial: " + svmKernelPolinomial(bagOfWords, classes)

  return output

def acc(scores):
  return "--> Acc: %0.2f%% (+/- %0.3f)" % (scores.mean() * 100, scores.std() * 2)

def naiveBayes(bow, classes):
  return acc(cross_validation.cross_val_score(naive_bayes.MultinomialNB(alpha=.01), bow, classes, cv=10))

def logistic(bow, classes):
  c = list((10.0**i) for i in range(-3,3))
  tuned_parameters = [{'C': c}]
  clf = GridSearchCV(linear_model.LogisticRegression(), tuned_parameters, cv=10)
  clf.fit(bow, classes)

  output = "\n--> Melhores parametros: --> C: %f\n" % (clf.best_estimator_.C)
  return output + acc(cross_validation.cross_val_score(linear_model.LogisticRegression(C=clf.best_estimator_.C), bow, classes, cv=10))

def svmLinear(bow, classes):
  c = list((10.0**i) for i in range(-3,3))
  tuned_parameters = [{'C': c}]
  clf = GridSearchCV(svm.LinearSVC(), tuned_parameters, cv=10)
  clf.fit(bow, classes)

  output = "\n--> Melhores parametros: --> C: %f\n" % (clf.best_estimator_.C)
  return output + acc(cross_validation.cross_val_score(svm.LinearSVC(C=clf.best_estimator_.C), bow, classes, cv=10))

def svmKernelLinear(bow, classes):
  c = list((10.0**i) for i in range(-3,3))
  tuned_parameters = [{'kernel': ['linear'], 'C': c}]
  clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=10)
  clf.fit(bow, classes)

  output = "\n--> Melhores parametros: --> C: %f\n" % (clf.best_estimator_.C)
  return output + acc(cross_validation.cross_val_score(svm.SVC(kernel=clf.best_estimator_.kernel,C=clf.best_estimator_.C), bow, classes, cv=10))

def svmKernelRadial(bow, classes):
  param = list((10.0**i) for i in range(-3,3))
  tuned_parameters = [{'kernel': ['rbf'], 'C': param, 'gamma': param}]
  clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=10)
  clf.fit(bow, classes)

  output = "\n--> Melhores parametros: --> C: %f \t Gamma: %f\n" % (clf.best_estimator_.C, clf.best_estimator_.gamma)
  return output + acc(cross_validation.cross_val_score(svm.SVC(kernel=clf.best_estimator_.kernel,C=clf.best_estimator_.C, gamma=clf.best_estimator_.gamma), bow, classes, cv=10))

def svmKernelPolinomial(bow, classes):
  param = list((10.0**i) for i in range(-3,3))
  tuned_parameters = [{'kernel': ['poly'], 'C': param, 'gamma': param}]
  clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=10)
  clf.fit(bow, classes)

  output = "\n--> Melhores parametros: --> C: %f \t Gamma: %f\n" % (clf.best_estimator_.C, clf.best_estimator_.gamma)
  return output + acc(cross_validation.cross_val_score(svm.SVC(kernel=clf.best_estimator_.kernel,C=clf.best_estimator_.C, gamma=clf.best_estimator_.gamma), bow, classes, cv=10))


  #encontra os vocabulos e torna-os unicos
  #texts = [set([word for word in document.lower().split()]) for document in documents]

  #monta dicionario pelo corpora do gensim
  #dictionary = corpora.Dictionary(texts)
  #print dictionary

  #transforma o vetor em bag of words
  #corpus = [dictionary.doc2bow(text) for text in texts]
  #print corpus

  #transforma vetor em matriz do NumPy e carrega como Table do Orange
  #numpy_matrix = gensim.matutils.corpus2dense(corpus,len(dictionary.keys()));
  #numpy_matrix = numpy_matrix.transpose()
  #numpy_classes = numpy.array([classes]).transpose()
  #numpy_matrix = numpy.hstack((numpy_matrix,numpy_classes))
  #d = Orange.data.Domain([Orange.feature.Discrete('a%i' % x, values=["0","1"])  for x in range(len(dictionary.keys())+1)])
  #data = Orange.data.Table(d,numpy_matrix)

  #data = list(data);

  #naive bayes
  #classifier = Orange.classification.bayes.NaiveLearner(data)
  #f = open('result_nb.txt','w')
  #for tweet in data:
      #tweet_id \t original \t classificado
      #f.write(str(tweets_id[data.index(tweet)])+'\t'+str(classifier(tweet))+'\t'+str(tweet.getclass())+'\n')

  #f.close()

  #svm
  #classifier = Orange.classification.svm.SVMLearner(data)
  #f = open('result_svm.txt','w')
  #for tweet in data:
      #tweet_id \t original \t classificado
      #f.write(str(tweets_id[data.index(tweet)])+'\t'+str(classifier(tweet))+'\t'+str(tweet.getclass())+'\n')

  #f.close()
