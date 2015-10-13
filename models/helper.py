import sqlite3

class Review(object):
    def __init__(self, uid, aid, rating):
        self.uid = uid
        self.aid = aid
        self.rating = rating
    
    def __repr__(self):
        return "<OBJECT RATING>: uid:{} aid:{} rating:{}".format(self.uid, self.aid, self.rating)

class Parse(object):
    def __init__(self, dbname):
        self.review_list = []
        self.dbname = dbname
        self.lines = self.get_sql_data()
        self.parse_lines(self.lines)
        
    def get_sql_data(self):
        dbname = self.dbname
        qry = """SELECT uid, aid, rating 
                FROM reviews 
                WHERE uid != '' 
                AND country != 'USA'"""
        with sqlite3.connect(dbname) as conn:
            cur = conn.cursor()
            cur.execute(qry)
            data = cur.fetchall()
        return data

    def parse_lines(self, lines):
        uids = set(map(lambda x: x[0], lines))
        uid_dict = dict(zip(uids, range(len(uids))))
        
        aids = set(map(lambda x: x[1], lines))
        aid_dict = dict(zip(aids, range(len(aids))))
        
        unique_reviews = self.get_unique_reviews(lines)
        
        for k,v in unique_reviews.iteritems():
            if not v[0]:
                continue
            uid = uid_dict[k[0]]
            aid = aid_dict[k[1]]
            rating = v[0]/float(v[1])
            self.review_list.append(Review(uid,aid,rating))
                    
    def get_unique_reviews(self, qry_lines):
        """
        Trip Advisor has duplicate reviews.  This averages the duplicate ratings.
        """
        newlist = {}
        for item in qry_lines:
            key = (item[0], item[1])
            if not newlist.get(key, None):
                newlist[key] = [item[2], 1]
            else:
                newlist[key][0] += item[2]
                newlist[key][1] += 1    
        return newlist