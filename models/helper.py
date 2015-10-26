import sqlite3
from datetime import datetime
from dateutil.parser import parse

class Review(object):
    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return "<OBJECT REVIEW>: uid:{} aid:{} rating:{}".format(self.uid, self.aid, self.rating)

class Parse(object):
    """
    A class to parse the database file.  Returns a list of Review objects.
    Calls get_sql_data() then parse_lines(lines)
    """
    def __init__(self, dbname):
        self.review_list = []
        self.nusers = None
        self.nitems = None
        self.dbname = dbname

        qrycols = ['key','country','uid','aid','name','rating','location','review_date','lang','user_home']
        qrycols = [ 'reviews.'+x for x in qrycols]
        qrycols.append('activities.tags')
        qrycols.append('activities.kgroup')
        self.qrycols = qrycols
        self.cols = [x.split('.')[1] for x in self.qrycols]

        lines = self.get_sql_data()
        self.review_list = self.parse_lines(lines)
        
        
    def get_sql_data(self):
        dbname = self.dbname
        qry = """SELECT {}
                FROM reviews 
                LEFT JOIN activities
                USING (aid)
                WHERE uid != '' 
                AND reviews.country != 'USA' 
                """.format(",".join(self.qrycols))

        with sqlite3.connect(dbname) as conn:
            cur = conn.cursor()
            cur.execute(qry)
            data = cur.fetchall()
        return data

    def parse_lines(self, lines):
        """
        Create review_list filled with Review objects
        """
        uid_idx = self.cols.index('uid')
        aid_idx = self.cols.index('aid')
        rate_idx = self.cols.index('rating')
        date_idx = self.cols.index('review_date')
        tag_idx = self.cols.index('tags')
        grp_idx = self.cols.index('kgroup')

        uids = set( [x[uid_idx] for x in lines] )
        self.nusers = len(uids)
        aids = set( [x[aid_idx] for x in lines] )
        self.nitems = len(aids)

        review_list = []

        for item in lines:
            item = list(item)
            
            if not item[rate_idx]:
                continue

            if item[grp_idx]:
                item[grp_idx] = [int(x) for x in item[grp_idx].split(',')]
            item[tag_idx] = [x.strip() for x in item[tag_idx].split(',')]
            item[date_idx] = parse(item[date_idx])

            d = dict(zip(self.cols, item))
            review_list.append(Review(d))
        return review_list
