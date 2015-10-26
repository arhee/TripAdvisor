
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
import pickle
import sqlite3

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
    
    def start(self, model):
        print model.__class__
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
        print 'test error: {}, train error {:.3f}, time {:.2f}mins'.format(test_err, train_err, (time()-t0)/60)
        return test_err


def round_to_1(x):
    return round(x, -int(floor(log10(x))))


def run():
    ############# Iniitiate Data ####################    
    
    print "reading data"
    dbname = '../data/mod_trip_advisor.db'
    #data = Parse(dbname)
    #pickle.dump( data, open( "tripadv.p", "wb" ) )

    ############# Load Data ####################
    #print "Loading Data...."
    #data = pickle.load(open("tripadv.p"))
    
    #nusers = len( set( map(lambda x: x.uid, data.review_list)) )
    #nitems = len( set( map(lambda x: x.aid, data.review_list)) )

    ############# Model Selection ####################
    
    # SVD
    #model = BiasSVD(nusers, nitems)
    #model = PlainSVD(nusers, nitems)
    #model = AidAverage()

    # Linear Models
    #model = BaseModel()
    #model = ItemModel()
    #model = ItemMonthModel()
    #selectmodel = SelectItemModel()
    
    #model = UserModel()
    #model = LangItemModel()
    #model = LangModel()
    #model = UserGroupModel()
    #model = SelectUserModel()

    #model = GroupModel()
    #basemodel = SelectUserModel()
    #UserGroupModel()

    model = CombinedModel()

    ############# Model Setup ####################

    print "Running Model ..."
    savename = 'usermodel1'

    model.verbose = False
    mw = ModelWrapper(data.review_list)
    mw.save_file = savename + '.npy'

    paramsearch = 0
    singlerun = 0
    featsearch = 0
    itemmonth = 0

    ############# Single Run ####################

    model.max_train_iters = 15
    model.lrate = 0.01
    model.reg_term = 0.01

    if singlerun:
        mw.start(model)

    ############# Feature Searching #############

    # Group Model Comparison 
    model.group = 0
    model.groupsize = 10
    attrlist = pickle.load(open('item_months1000.p'))
    model.aid_list = [x[0] for x in attrlist]
    mw.start(model)


    #mw.start(basemodel)


    # Finding month/aid combinatorial biases 
    """
    if itemmonth:
        attrlist = pickle.load(open('item_months1000.p'))
        model.items = [x[0] for x in attrlist]
        mw.start(model)

        selectmodel.items = model.items
        mw.start(selectmodel)
    """

    #Search for attractions that give benefit
    """
    aid_list = pickle.load(open('attr100.p'))
    results = []
    for ix, item in enumerate(aid_list):
        
        #abias
        selectmodel.items = [item]
        err = mw.start(selectmodel)
        #print '-'*10, 'abias'
        #print singlemodel.abias
        
        #monthbias
        model.items = [item]
        month_err = mw.start(model)
        #print '-'*10, 'ambias'
        #print model.ambias
        
        diff = month_err - err
        print 'item #:', ix, 'diff: ', diff
        if month_err < err:
            print "\n Added! {:.3f}".format(diff)
            results.append((item, diff))

    pickle.dump( results, open( "item_months100.p", "wb" ) )
    """
    
    #Look for biases in months
    """
    months = range(1,13)
    for month in months:
        model.mbias = {month:0}
        if mw.start(model) < err:
            print 'added ', month
            selected.append(month)
    """

    #iterate to find language biases
    """   
    langlist = [u'en', u'fr', u'ru', u'ro', u'it', u'ja', u'nl', u'es', u'pt',
       u'de', u'ko', u'vi', u'da', u'zh-tw', u'no', u'zh-cn', u'id', u'th',
       u'pl', u'he', u'el', u'sv', u'tr', u'af', u'fi', u'hu', u'cs',
       u'et', u'ar', None, u'ca', u'so', u'mk', u'sl', u'sk', u'bg', u'cy',
       u'tl']
    err = round(mw.start(basemodel), 3)

    selected = []
    for lang in langlist:
        model.lbias = {lang:0}
        if mw.start(model) < err:
            print "added ", lang
            selected.append(lang)

    print selected
    """

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
