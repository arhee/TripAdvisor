import pandas as pd
import numpy as np
from sklearn.linear_model import Lasso, ElasticNet, Ridge, LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from itertools import product
from time import time
import pickle
from pprint import pprint

import sys

class Average(object):
    def __init__(self):
        self.avg = None
    
    def fit(self, X, y):
        self.avg = np.mean(y)
    
    def predict(self, x):
        return np.array([self.avg] *  x.shape[0])

def find_err(kfdf, Xcols, model):
    """
    kfdf is a list containing the kfolds dataframes for test/train.
    Xcols in the list of column names to choose from
    for dataframe format
    """
    error = 0.
    for fold in kfdf:
        X_train = fold['train']['x'][:, Xcols]
        y_train = fold['train']['y']
        X_test = fold['test']['x'][:, Xcols]
        y_test = fold['test']['y']

        model.fit(X_train, y_train.T.toarray().flatten())
    	err = model.predict(X_test).flatten() - y_test.toarray().flatten()
        error +=  (sum(err**2)/len(err))**0.5
    return error/len(kfdf), model

#load the data
print "reading data..."
with open('kfolds5notnorm.p') as f:
    kfdf = pickle.load(f)


#model = Ridge()
#model = Lasso(fit_intercept=True)
#model = Average()
#model = ElasticNet()
#model = LogisticRegression()
model = RandomForestClassifier()
nfeats = kfdf[0]['train']['x'].shape[1]
goodfeats= set([])
scores = []
features = []


print "starting search..."

#while (len(goodfeats) < 2): 
goodfeats.update([818])
test = []
for idx in range(nfeats):
	addfeat = [0,10]
	for feat in range(nfeats):
		if feat in goodfeats: continue

		Xcols = list(goodfeats)
		Xcols.append(feat)
		feat_score, modelfit = find_err(kfdf, Xcols, model)

		test.append([feat, feat_score])

		if feat_score < addfeat[1]:
			addfeat = [feat, feat_score]
	print 'finished loop', idx, addfeat

	if not scores:
		scores.append(addfeat[1])
		goodfeats.update([addfeat[0]])
		features.append(addfeat)
	elif scores and scores[-1] - addfeat[1] > 0:
		scores.append(addfeat[1])
		goodfeats.update([addfeat[0]])
		features.append(addfeat)
	else:
		break
