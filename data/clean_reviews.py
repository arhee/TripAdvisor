import sqlite3
import pandas as pd
import time
import string
from nltk.stem import SnowballStemmer
import sys
import itertools
from nltk.corpus import stopwords

class Cleaner(object):
	def __init__(self):
		self.sbstem = SnowballStemmer("english")
		replace = string.punctuation + string.digits
		self.replace_punctuation = string.maketrans(replace, ' '*len(replace))
		self.locations = []
		self.cached_stopwords = stopwords.words("english")

	def clean(self, txt):
		#removes stopwords, punctuation
	    txt = txt.encode('ascii','ignore')
	    nopunct = txt.translate(self.replace_punctuation)
	    no_locs = [x for x in nopunct.split() if x.lower() not in self.cached_stopwords]
	    stemmed = [self.sbstem.stem(x) for x in no_locs]
	    return " ".join(stemmed)

	def make_loclist(self, locations):
		locations = list(locations)
		removelist = ['Ho Chi Minh City', 'Phu Quoc Island', 'Halong Bay']
		locations = [x.lower() for x in locations if x not in removelist]		
		locations.extend(['ho chi minh','hoan','kiem','phu quoc', 'halong', 'vietnam', 'dong','vnd','vdn'])
		locations.extend(['vietnames', 'nhatrang','saigon','america','maryland','york'])
		loc_wordlist = [f.split() for f in locations]
		loc_wordlist = list(itertools.chain(*loc_wordlist))
		self.cached_stopwords.extend(loc_wordlist)
		return loc_wordlist

def get_reviews(dbname):
	with sqlite3.connect(dbname) as conn:
	    cur = conn.cursor()
	    # can edit qry to select items with > reviews
	    qry = """SELECT key, review_text, title, location
	            FROM reviews
	            WHERE lang = 'en'
	            AND country = "Laos"
	            """
	    cur.execute(qry)
	    data = cur.fetchall()
	return data

def combine_strings(x):
    doc = []
    for item in x:
        doc.append(item)
    return " ".join(doc)

def db_insert_text(dbname, text, key):
	with sqlite3.connect(dbname) as conn:
	    cur = conn.cursor()
	    qry = """UPDATE OR IGNORE reviews SET clean_review_text = ?
	    			WHERE key = ?"""
	    cur.execute(qry, [text, key])
	    conn.commit()

#if __name__ == "__main__":
print "Retrieving Reviews"
fname = 'mod_trip_advisor.db'
data = get_reviews(fname)

cleaner = Cleaner()
locations = set([x[3] for x in data])
cleaner.make_loclist(locations)
	
t0 = time.time()
print "Starting Loop\n"

subt0 = t0

for idx, review in enumerate(data):
	if not idx % 1000:
		sys.stdout.flush()
		elapsed = (time.time() - subt0)/60
		sys.stdout.write('\r idx:{}, elapsed time:{:.2f}min'.format(idx, elapsed))
		subt0 = time.time()
	key = review[0]
	review_text = review[1]
	title = review[2]

	text = review_text + title

	cleaned = cleaner.clean(text)
	db_insert_text(fname, cleaned, key)

print "total time: {:.2f}mins".format((time.time()-t0)/60)

