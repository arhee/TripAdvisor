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


class AidAverage(Model):
    """
    Model predicts on average for the attraction
    """
    def __init__(self):
        super(AidAverage, self).__init__()        

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


################### Bias Models ######################

class BaseModel(Model):
    """
    This is the base model: r = global_avg
    """
    def __init__(self):
        super(BaseModel, self).__init__()

    def train(self, review_list):
        self.review_list = review_list
        self.setup()
        iter_error = float('inf')

        for _ in range(self.max_train_iters):
            self.stoc_grad_desc()
            rmse = round(self.get_rmse(), 3)
            if rmse >= iter_error:
                break
            else:
                iter_error = rmse

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
        pred = self.avg 
        err = review.rating - pred    
        return err**2

    def predict(self, review):
        return self.proper_rating(self.avg)

    def setup(self):
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

class ItemModel(BaseModel):
    """
    r = global_avg + item_bias(item)
    """
    def __init__(self):
        super(ItemModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.abias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.aid not in self.abias:
            self.abias[review.aid] = 0
        bi = self.abias[review.aid]
        pred = self.avg + bi
        err = review.rating - pred    
        self.abias[review.aid] += self.lrate * (err - self.reg_term * bi)
        return err**2

    def predict(self, review):
        bi = self.abias.get(review.aid,0)
        return self.proper_rating(self.avg + bi)


class LangItemModel(BaseModel):
    """
    r = global_avg + item_bias(item) + lang_bias(lang)
    """
    def __init__(self):
        super(LangItemModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        self.lbias = {'ja':0}
        self.abias = {}

    def iterate(self, review):
        bl = 0
        if review.lang in self.lbias:
            bl = self.lbias[review.lang]

        if review.aid not in self.abias:
            self.abias[review.aid] = 0
        bi = self.abias[review.aid]

        pred = self.avg + bl + bi
        err = review.rating - pred    

        if review.lang in self.lbias:
            self.lbias[review.lang] += self.lrate * (err - self.reg_term * bl)
        self.abias[review.aid] += self.lrate * (err - self.reg_term * bi)
        return err**2

    def predict(self, review):
        bl = self.lbias.get(review.lang,0)
        bi = self.abias.get(review.aid,0)
        return self.proper_rating(self.avg + bi + bl)


class LangModel(BaseModel):
    """
    r = global_avg + lang_bias(lang)
    """
    def __init__(self):
        super(LangModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        self.lbias = {'ja':0}

    def iterate(self, review):
        if not review.lang in self.lbias:
            return (review.rating - self.avg)**2
        bl = self.lbias[review.lang]
        pred = self.avg + bl
        err = review.rating - pred    
        self.lbias[review.lang] += self.lrate * (err - self.reg_term * bl)
        return err**2

    def predict(self, review):
        return self.proper_rating(self.avg + self.lbias.get(review.lang,0))        

class UserModel(BaseModel):
    """
    r = global_avg + user_bias(user)
    """
    def __init__(self):
        super(UserModel, self).__init__()
        #self.nusers = nusers
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.ubias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.uid not in self.ubias:
            self.ubias[review.uid] = 0
        bu = self.ubias[review.uid]
        pred = self.avg + bu
        err = review.rating - pred    
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2

    def predict(self, review):
        bu = 0.
        if review.uid in self.ubias:
            bu = self.ubias[review.uid]
        return self.proper_rating(self.avg + bu)


class SelectUserModel(BaseModel):
    """
    r = global_avg + user_bias(user_from_uidset)
    """
    def __init__(self):
        super(SelectUserModel, self).__init__()
        self.uidset = None
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.ubias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.uid not in self.uidset:
            return (self.avg - review.rating)**2

        if review.uid not in self.ubias:
            self.ubias[review.uid] = 0
        bu = self.ubias[review.uid]
        pred = self.avg + bu
        err = review.rating - pred    
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2

    def predict(self, review):
        if review.uid not in self.uidset:
            return self.avg
        bu = 0.
        if review.uid in self.ubias:
            bu = self.ubias[review.uid]
        return self.proper_rating(self.avg + bu)


class SelectItemModel(BaseModel):
    """
    r = global_avg + item_bias(item)
    """
    def __init__(self):
        super(SelectItemModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        self.abias = dict(zip(self.items, [0]*len(self.items)))

    def iterate(self, review):
        if not review.aid in self.abias:
            return (review.rating - self.avg)**2

        bi = self.abias[review.aid]
        pred = self.avg + bi
        err = review.rating - pred    
        self.abias[review.aid] += self.lrate * (err - self.reg_term * bi)
        return err**2

    def predict(self, review):
        abias = self.abias.get(review.aid, 0)
        return self.proper_rating(self.avg + abias)

class ItemMonthModel(BaseModel):
    """
    r = global_avg + month_loc_bias(location, month)
    """
    def __init__(self):
        super(ItemMonthModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        emptydicts = [np.zeros(12) for _ in range(len(self.items))]
        self.ambias = dict(zip(self.items, emptydicts))

    def iterate(self, review):
        if not review.aid in self.items:
            return (review.rating - self.avg)**2
        bam = self.ambias[review.aid][review.review_date.month-1]
        pred = self.avg + bam
        err = review.rating - pred    
        self.ambias[review.aid][review.review_date.month-1] += self.lrate * (err - self.reg_term * bam)
        return err**2

    def predict(self, review):
        if review.aid in self.ambias:
            bias = self.ambias[review.aid][review.review_date.month-1]
        else:
            bias = 0

        return self.proper_rating(self.avg + bias)

class UserTagModel(BaseModel):
    """
    r = global_avg + user_group_bias(user, tags)
    """
    def __init__(self):
        super(UserGroupModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01
        self.uidset = None

    def setup(self):
        self.ubias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.uid not in self.uidset:
            return (review.rating - self.avg)**2

        if not review.uid in self.ubias:
            self.ubias[review.uid] = {}

        bias = 0.
        for tag in review.tags:
            if tag in self.ubias[review.uid]:
                bias += self.ubias[review.uid][tag]
            else:
                self.ubias[review.uid][tag] = 0

        pred = self.avg + bias
        err = review.rating - pred    

        for tag in review.tags:
            bias = self.ubias[review.uid][tag]
            self.ubias[review.uid][tag] += self.lrate * (err - self.reg_term * bias)
        return err**2

    def predict(self, review):
        if review.uid not in self.uidset:
            return self.proper_rating(self.avg)

        bias = 0.
        if review.uid in self.ubias:
            for tag in review.tags:
                bias += self.ubias[review.uid].get(tag, 0)
        return self.proper_rating(self.avg + bias)

class UserGroupModel(BaseModel):
    """
    r = global_avg + user_group_bias(user, group) + user_bias(user)
    """
    def __init__(self):
        super(UserGroupModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01
        self.uidset = None

        #group is idx, groupsize is kmeans cluster size
        self.group = None
        self.groupsize = None

    def setup(self):
        self.gbias = {}
        self.ubias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.uid not in self.uidset or not review.kgroup:
            return (review.rating - self.avg)**2

        #if the user dict does not contain records of the user
        if not review.uid in self.gbias:
            self.gbias[review.uid] = np.zeros(self.groupsize)
            self.ubias[review.uid] = 0

        kgrp = review.kgroup[self.group] - 1
        bg = self.gbias[review.uid][kgrp]
        bu = self.ubias[review.uid]

        pred = self.avg + bg + bu
        err = review.rating - pred    

        self.gbias[review.uid][kgrp] += self.lrate * (err - self.reg_term * bg)
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2

    def predict(self, review):
        if review.uid not in self.gbias or not review.kgroup:
            return self.proper_rating(self.avg)

        kgrp = review.kgroup[self.group] - 1
        bg = self.gbias[review.uid][kgrp]
        bu = self.ubias[review.uid]
        return self.proper_rating(self.avg + bg + bu)

class GroupModel(BaseModel):
    """
    r = global_avg + user_group_bias(user, group)
    """
    def __init__(self):
        super(GroupModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01
        self.uidset = None

        #group is idx, groupsize is kmeans cluster size
        self.group = None
        self.groupsize = None

    def setup(self):
        self.ubias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)

    def iterate(self, review):
        if review.uid not in self.uidset or not review.kgroup:
            return (review.rating - self.avg)**2

        #if the user dict does not contain records of the user
        if not review.uid in self.ubias:
            self.ubias[review.uid] = np.zeros(self.groupsize)
        kgrp = review.kgroup[self.group] - 1
        bg = self.ubias[review.uid][kgrp]

        pred = self.avg + bg
        err = review.rating - pred    

        self.ubias[review.uid][kgrp] += self.lrate * (err - self.reg_term * bg)
        return err**2

    def predict(self, review):
        if review.uid not in self.ubias or not review.kgroup:
            return self.proper_rating(self.avg)

        kgrp = review.kgroup[self.group] - 1
        return self.proper_rating(self.avg + self.ubias[review.uid][kgrp])

class CombinedModelAll(BaseModel):
    def __init__(self):
        super(CombinedModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.ubias = {}
        self.gbias = {}
        self.abias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        emptydicts = [np.zeros(12) for _ in range(len(self.aid_list))]
        self.ambias = dict(zip(self.aid_list, emptydicts))


    def iterate(self, review):
#        if review.uid not in self.ubias:
#            self.ubias[review.uid] = 0

        # ambias takes priority.  Leftovers go into abias.
        bam = 0.
        ba = 0.
        if review.aid in self.ambias:
            bam = self.ambias[review.aid][review.review_date.month-1]
        elif review.aid not in self.abias:
            self.abias[review.aid] = 0
        else:
            ba = self.abias[review.aid]


        # gbias takes priority over ubias
        bg = bu = 0
        if review.kgroup:
            if not review.uid in self.gbias:
                self.gbias[review.uid] = np.zeros(self.groupsize)
            kgrp = review.kgroup[self.group] - 1
            bg = self.gbias[review.uid][kgrp]
        else:
            if not review.uid in self.ubias:
                self.ubias[review.uid] = 0
            bu = self.ubias[review.uid]


        #bu = self.ubias[review.uid]
        pred = self.avg + ba + bam + bg + bu
        err = review.rating - pred 

        #self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)

        if review.aid in self.ambias:
            self.ambias[review.aid][review.review_date.month-1] += self.lrate * (err - self.reg_term * bam)
        else:
            self.abias[review.aid] += self.lrate * (err - self.reg_term * ba)

        if review.kgroup:
            kgrp = review.kgroup[self.group] - 1
            self.gbias[review.uid][kgrp] += self.lrate * (err - self.reg_term * bg)
        else:
            self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)

        return err**2

    def predict(self, review):
        if review.kgroup and review.uid in self.gbias:
            kgrp = review.kgroup[self.group] - 1
            bu = self.gbias[review.uid][kgrp]
        else:
            bu = self.ubias.get(review.uid, 0)

        ba = self.abias.get(review.aid, 0)

        bam = 0.
        if review.aid in self.ambias:
            bam = self.ambias[review.aid][review.review_date.month-1]

        return self.proper_rating(self.avg + bu + ba + bam)


class CombinedModel(BaseModel):
    def __init__(self):
        super(CombinedModel, self).__init__()
        self.lrate = 0.01
        self.reg_term = 0.01

    def setup(self):
        self.ubias = {}
        self.abias = {}
        self.avg = self.avg_rating()
        self.size = len(self.review_list)
        emptydicts = [np.zeros(12) for _ in range(len(self.aid_list))]
        self.ambias = dict(zip(self.aid_list, emptydicts))
        self.lbias = {'ja':0}


    def iterate(self, review):
        if review.uid not in self.ubias:
            self.ubias[review.uid] = 0

        bl = 0.
        if review.lang in self.lbias:
            bl = self.lbias[review.lang]
        
        # ambias takes priority.  Leftovers go into abias.
        bam = 0.
        ba = 0.
        if review.aid in self.ambias:
            bam = self.ambias[review.aid][review.review_date.month-1]
        elif review.aid not in self.abias:
            self.abias[review.aid] = 0
        else:
            ba = self.abias[review.aid]

        bu = self.ubias[review.uid]
        pred = self.avg + ba + bam + bu + bl
        err = review.rating - pred 

        #self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)

        if review.aid in self.ambias:
            self.ambias[review.aid][review.review_date.month-1] += self.lrate * (err - self.reg_term * bam)
        else:
            self.abias[review.aid] += self.lrate * (err - self.reg_term * ba)
        
        if review.lang in self.lbias:
            self.lbias[review.lang] += self.lrate * (err - self.reg_term * bl)
        
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * bu)
        return err**2

    def predict(self, review):
        bu = self.ubias.get(review.uid, 0)
        ba = self.abias.get(review.aid, 0)
        bl = self.lbias.get(review.lang, 0)
        bam = 0.
        if review.aid in self.ambias:
            bam = self.ambias[review.aid][review.review_date.month-1]

        return self.proper_rating(self.avg + bu + ba + bam + bl)    


################# The SVD class of models #####################

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
    # to check this.  I need to compare against both linear and SVD.  They're both working

    def __init__(self, nusers, nitems):    
        super(BiasSVD, self).__init__(nusers, nitems)
        self.initval = 0
        # ubias, abias are located in SVD.setup()

    def iterate(self, review, k):
        err = review.rating - self.cached_predict(review, k)
        self.err_track.update(err**2)

        uTemp = self.U[review.uid][k]
        vTemp = self.V[review.aid][k]
        ubias = self.ubias[review.uid]
        abias = self.abias[review.aid]

        self.U[review.uid][k] += self.lrate * (err*vTemp - self.reg_term*uTemp)
        self.V[review.aid][k] += self.lrate * (err*uTemp - self.reg_term*vTemp)
        self.ubias[review.uid] += self.lrate * (err - self.reg_term * ubias)
        self.abias[review.aid] += self.lrate * (err - self.reg_term * abias)
        return err**2

    def predict(self, review):
        uid = review.uid
        aid = review.aid
        return self.proper_rating( sum(self.U[uid] * self.V[aid]) + self.ubias[uid] + self.abias[aid] + self.avg)

    def cached_predict(self, review, k):
        uid = review.uid
        aid = review.aid
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
