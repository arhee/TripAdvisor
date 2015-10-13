import numpy as np
import sys
import random
from time import time, sleep


class ErrorTracker(object):
    def __init__(self):
        self.count = 0
        self.err = 0

    def update(self, x):
        self.count += 1
        self.err += x

    def reset(self):
        self.count = 0
        self.err = 0

    def get_err(self):
        return (self.err/self.count) ** 0.5

class Model(object):
    def __init__(self):
        self.review_list = None
        self.verbose = False
        self.max_train_iters = 1
        self.print_iter = 10000
        self.err_track = ErrorTracker()

    def test(self, review_list):                         
        err = [ (self.predict(review) - review.rating)**2 for review in review_list]
        return (sum(err)/len(err))**0.5

    def get_rmse(self):
        err = 0.
        for review in self.review_list:
            err += (review.rating - self.predict(review))**2
        return (err/self.size)**0.5
                
    def avg_rating(self):
        total = 0.
        for review in self.review_list:
            total += review.rating
        return total/len(self.review_list)

    def proper_rating(self, x):
        if x > 5: return 5.
        elif x < 1: return 1.
        return x


class Average(Model):
    def __init__(self):
        super(Average, self).__init__()        

    def setup(self):
        self.avg = self.avg_rating()
        self.avgdict = {}
        self.size = len(self.review_list)

    def train(self, review_list):
        self.review_list = review_list
        self.setup()

        for review in self.review_list:
            aid = review.aid
            if not self.avgdict.get(aid, None):
                self.avgdict[aid] = {'sum':review.rating, 'count':1}
            else:
                self.avgdict[aid]['sum'] += review.rating
                self.avgdict[aid]['count'] += 1

        for k,v in self.avgdict.iteritems():
            self.avgdict[k] = v['sum']/v['count']

        if self.verbose:
            print "Total Training RMSE {:.3f}".format(self.get_rmse())

    def predict(self, review):
        return self.avgdict.get(review.aid, self.avg)


class LinearModel(Model):
    def __init__(self, nusers, nitems):
        super(LinearModel, self).__init__()
        self.nitems = nitems
        self.nusers = nusers
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.ubias = np.zeros(self.nusers)
        self.abias = np.zeros(self.nitems)
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def train(self, review_list):
        self.review_list = review_list
        self.setup()
        for _ in range(self.max_train_iters):
            self.stoc_grad_desc()
        if self.verbose:
            print "Total Training RMSE {:.3f}".format(self.get_rmse())

    def stoc_grad_desc(self):
        self.err_track = ErrorTracker()
        for idx, review in enumerate(self.review_list):
            if self.verbose and idx > 0 and not idx % self.print_iter:
                print "iteration #:{} smoothed error: {:.3f}".format(idx, self.err_track.get_err())
                self.err_track.reset()
            self.err_track.update( self.iterate(review) )

    def iterate(self, review):
        bi = self.abias[review.aid]
        bu = self.ubias[review.uid]
        pred = self.avg + bi + bu
        err = review.rating - pred    
        self.abias[review.aid] += self.lrate * (err - self.reg_term * bi)
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2

    def predict(self, review):
        return self.avg + self.abias[review.aid] + self.ubias[review.uid]

class NeighborSearch(Model):
    def __init__(self, nusers, nitems):
        self.uid_dict = {}
        self.weight = np.zeros(nitems, nitems)
        pass

    def train(self, review_list):
        self.review_list = review_list        
        self.setup()
        self.get_uid_dict()
        for _ in range(self.max_train_iters):
            self.stoc_grad_desc()
        if self.verbose:
            print "Total Training RMSE {:.3f}".format(self.get_rmse())


    def get_uid_dict(self):
        for idx, review in enumerate(self.review_list):
            if not self.uid_dict.get(review.uid, None):
                self.uid_dict[review.uid] = [idx]
            else:
                self.uid_dict[review.uid].append(idx)
            

    def stoc_grad_desc(self):
        self.err_track = ErrorTracker()
        for idx, review in enumerate(self.review_list):
            if self.verbose and idx > 0 and not idx % self.print_iter:
                print "iteration #:{} smoothed error: {:.3f}".format(idx, self.err_track.get_err())
                self.err_track.reset()
            self.err_track.update( self.iterate(review) )

    def iterate(self, review):
        bi = self.abias[review.aid]
        bu = self.ubias[review.uid]
        pred = self.avg + bi + bu
        err = review.rating - pred    
        self.abias[review.aid] += self.lrate * (err - self.reg_term * bi)
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2


class SVD(Model):
    def __init__(self, nusers, nitems): 
        super(SVD, self).__init__()   
        self.nitems = nitems
        self.nusers = nusers

        self.nfeats = 10
        self.lrate = 0.04
        self.reg_term = 0.01
        self.initbias = 0


    def setup(self):
        self.size = len(self.review_list)
        
        self.avg = self.avg_rating()
        self.initval = (self.avg/self.nfeats) ** 0.5        

        self.U = np.empty([self.nusers, self.nfeats])
        self.U.fill(self.initval)
        self.V = np.empty([self.nitems, self.nfeats])
        self.V.fill(self.initval)

        self.cache = np.empty([self.nusers, self.nitems])
        self.ubias = np.zeros(self.nusers)
        self.abias = np.zeros(self.nitems)

    def stoc_grad_desc(self, k):
        self.err_track = ErrorTracker()
        for idx, review in enumerate(self.review_list):
            if self.verbose and idx > 0 and not idx % self.print_iter:
                print "iteration #:{} error: {:.3f}".format(idx, self.err_track.get_err())
                self.err_track.reset()
            self.iterate(review, k)


    def train(self, review_list):
        """
        Iterate over
            - features
            - stochastic gradient descent
        """
        self.review_list = review_list
        self.setup()

        prev_err = 0        
        for k in range(self.nfeats):
            random.shuffle(self.review_list)

            for iters in range(self.max_train_iters):
                t0 = time()
                self.stoc_grad_desc(k)
                if self.verbose:
                    sys.stdout.flush()
                    sys.stdout.write('\rfinished feature:{} time:{:.2f}secs'.format(k+1, time()-t0))
            self.update_cache(k)

    def update_cache(self, k):
        for review in self.review_list:
            uid = review.uid
            aid = review.aid
            self.cache[uid][aid] += self.U[uid][k] * self.V[aid][k]


class BiasSVD(SVD):
    def __init__(self, nusers, nitems):    
        super(BiasSVD, self).__init__(nusers, nitems)
        self.lrate = 0.01

    def iterate(self, review, k):
        err = review.rating - self.cached_predict(review.uid, review.aid, k)
        self.err_track.update(err**2)

        uTemp = self.U[review.uid][k]
        vTemp = self.V[review.aid][k]
        ubias = self.ubias[review.uid]
        abias = self.abias[review.aid]

        self.U[review.uid][k] += self.lrate * (err*vTemp - self.reg_term*uTemp)
        self.V[review.aid][k] += self.lrate * (err*uTemp - self.reg_term*vTemp)
        self.ubias[review.uid] += self.lrate * (err + self.reg_term * ubias)
        self.abias[review.aid] += self.lrate * (err + self.reg_term * abias)

        return err**2


    def predict(self, review):
        uid = review.uid
        aid = review.aid
        return self.proper_rating( sum(self.U[uid] * self.V[aid]) + self.ubias[uid] + self.abias[aid] + self.avg)

    def cached_predict(self, uid, aid, k):
        after = (self.nfeats-k-1) * self.initval**2
        current = self.U[uid][k] * self.V[aid][k]
        before = self.cache[uid][aid]
        return self.proper_rating(after + current + before + self.ubias[uid] + self.abias[aid] + self.avg)


class PlainSVD(SVD):
    """
    Parameters:
    reg_term
    lrate
    nfeats
    max_train_iters
    """

    def iterate(self, review, k):
        err = review.rating - self.cached_predict(review.uid, review.aid, k)
        self.err_track.update(err**2)

        uTemp = self.U[review.uid][k]
        vTemp = self.V[review.aid][k]
        self.U[review.uid][k] += self.lrate * (err*vTemp - self.reg_term*uTemp)
        self.V[review.aid][k] += self.lrate * (err*uTemp - self.reg_term*vTemp)


    def predict(self, review):
        uid = review.uid
        aid = review.aid
        return self.proper_rating( sum(self.U[uid] * self.V[aid]) )

    def cached_predict(self, uid, aid, k):
        after = (self.nfeats-k-1) * self.initval**2
        current = self.U[uid][k] * self.V[aid][k]
        before = self.cache[uid][aid]
        return self.proper_rating(after + current + before)
