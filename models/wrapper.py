
"""
This is a wrapper class to execute models from models.py

Ref: Improving regularized singular value decomposition for
collaborative filtering with implementation of biases
"""

import numpy as np
from numpy import log10
import sys
import random
from time import time, sleep
from helper import Parse, Review
from models import *
from itertools import product, izip
import json
import pdb

from sklearn import cross_validation
from math import log10, floor


class ModelWrapper(object):
    def __init__(self, review_list):
        self.cv_iters = 1
        self.SEED = 1000
        self.mean_error = 0.
        self.test_size = 0.2
        self.review_list = review_list
        self.save_file = None

    def get_ratings(self, mylist):
        return [review.rating for review in mylist]

    def attr_combs(self, dicts):
        return (dict(izip(dicts, x)) for x in product(*dicts.itervalues()))

    def param_search(self, model, params):
        #Params are in dict format {'a':[1,2,3], 'b':range(40,45), 'c':range(5,9)}
        
        varspace = [len(x) for x in params.values()] 
        data = np.empty(varspace)
        for attrdict in self.attr_combs(params):
            indices = [0] * len(params)
            for param_name, value in attrdict.iteritems():
                model.__dict__[param_name] = value
                param_loc = params.keys().index(param_name)
                indices[param_loc] = params[param_name].index(value)

            print "\nparameters: ", attrdict
            data[tuple(indices)] = self.start(model)

            with open(self.save_file,'w') as f:    
                np.save(f, data)

        return data

    
    def output_preds(self, model):
        mean_error = 0.
        train_error = 0.

        t0 = time()
        
        if model.verbose:
            sys.stdout.flush()
            sys.stdout.write('\r CV loop #{}\n'.format(i+1))

        kf = cross_validation.KFold(len(self.review_list), n_folds=5, shuffle=True, random_state = 0)
        for train_idx, test_idx in kf:

            test_list = [ self.review_list[idx] for idx in test_idx ]
            train_list = [ self.review_list[idx] for idx in train_idx ]

            model.train(train_list)
            train_error += model.get_rmse()
            mean_error += model.test(test_list)
            
        test_err = mean_error/5
        train_err = train_error/5

        print 'test error: {:.3f}, train error {:.3f}, time {:.2f}mins'.format(test_err, train_err, (time()-t0)/60)
        return test_err

    
    def start(self, model):
        mean_error = 0.
        train_error = 0.
        t0 = time()
        
        kf = cross_validation.KFold(len(self.review_list), n_folds=5, shuffle=True, random_state = 0)

        for train_idx, test_idx in kf:
            test_list = [ self.review_list[idx] for idx in test_idx ]
            train_list = [ self.review_list[idx] for idx in train_idx ]

            model.train(train_list)
            train_error += model.get_rmse()
            mean_error += model.test(test_list)
    
        test_err = mean_error/5
        train_err = train_error/5
        print 'test error: {:.3f}, train error {:.3f}, time {:.2f}mins'.format(test_err, train_err, (time()-t0)/60)
        return test_err


def round_to_1(x):
    return round(x, -int(floor(log10(x))))


def run():
    
    #############Load Data####################

    print "Loading Data...."
    data = Parse('../data/mod_trip_advisor.db')
    #nusers = len( set( map(lambda x: x.uid, data.review_list)) )
    nitems = len( set( map(lambda x: x.aid, data.review_list)) )

    ############# Model Selection ####################
    
    #model = BiasSVD(nusers, nitems)
    #model = PlainSVD(nusers, nitems)
    #model = AidAverage()

    #model = BaseModel()
    model = ItemModel(nitems)
    #model = UserModel(nusers)    
    #model = SimpleModel(nusers, nitems)

    ############# Model Setup ####################

    print "Running Model ..."
    savename = 'usermodel1'

    model.verbose = False
    mw = ModelWrapper(data.review_list)
    mw.save_file = savename + '.npy'

    paramsearch = False
    singlerun = True

    ############# Single Run ####################

    model.max_train_iters = 10
    model.lrate = 0.01
    model.reg_term = 0.01

    if singlerun:
        mw.start(model)

    ############# Parameter Search ####################
    
    #reg_terms = [round_to_1(x) for x in np.logspace(log10(0.003), log10(0.03), num=5)]
    #reg_terms = [round_to_1(x) for x in np.logspace(log10(0.001), log10(0.1), num=3)]
    #lrates = [round_to_1(x) for x in np.logspace(log10(0.001), log10(0.1), num=5)]
    #lrates = [round_to_1(x) for x in np.linspace(0.001, 0.01, num=10)]
    #max_train_iters = [3,5,7]
    #nfeats = [10]
    
   
    if paramsearch:
        params = {'nfeats':nfeats, 'lrate':lrates}
        with open(savename + '.json','w') as f:
            json.dump(params.items(), f)
        mw.param_search(model, params)

if __name__ == '__main__':
    run()



"""
SVD
parameters:  {'nfeats': 10, 'lrate': 0.01, maxtrain: 5, lrate:0.01}
test error: 0.761, train error 0.635, time 13.61mins
"""
