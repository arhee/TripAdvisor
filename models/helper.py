import sqlite3
from datetime import datetime
from dateutil.parser import parse

class Review(object):
    def __init__(self, uid, aid, rating, date, lang):
        self.uid = uid
        self.aid = aid
        self.rating = rating
        self.date = date
        self.lang = lang
    
    def __repr__(self):
        return "<OBJECT RATING>: uid:{} aid:{} rating:{} date:{}".format(self.uid, self.aid, self.rating, self.date)

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

        lines = self.get_sql_data()
        self.review_list = self.parse_lines(lines)
        
    def get_sql_data(self):
        dbname = self.dbname
        qry = """SELECT uid, aid, rating, review_date, lang
                FROM reviews 
                WHERE uid != '' 
                AND country != 'USA'"""

        with sqlite3.connect(dbname) as conn:
            cur = conn.cursor()
            cur.execute(qry)
            data = cur.fetchall()
        return data

    def parse_lines(self, lines):
        """
        uid_dict/aid_dict assigns an index number to the uid and aid
        """
        uids = set(map(lambda x: x[0], lines))
        uid_dict = dict(zip(uids, range(len(uids))))
        self.nusers = len(uids)
        
        aids = set(map(lambda x: x[1], lines))
        aid_dict = dict(zip(aids, range(len(aids))))
        self.nitems = len(aids)
        
        unique_reviews = self.get_unique_reviews(lines)
        review_list = []
        
        for k,v in unique_reviews.iteritems():
            if not v[0]:
                continue
            uid = uid_dict[k[0]]
            aid = aid_dict[k[1]]
            rating = v[0]/float(v[1])
            date = v[2]
            lang = v[3]
            review_list.append(Review(uid,aid,rating, date, lang))

        return review_list

                    
    def get_unique_reviews(self, qry_lines):
        """
        Trip Advisor has duplicate reviews.  This function averages the duplicate ratings.
        returns a dict {(uid,aid): [rating, #reviews]}
        """
        newlist = {}
        for item in qry_lines:
            key = (item[0], item[1])
            date = parse(item[3])
            lang = item[4]
            if not newlist.get(key, None):
                newlist[key] = [item[2], 1, date, lang]
            else:
                newlist[key][0] += item[2]
                newlist[key][1] += 1    
        return newlist