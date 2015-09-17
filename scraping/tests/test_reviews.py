import unittest
import os
import sqlite3
from ..bin.reviews import Review, ReviewList
from ..bin.schema import vietnam_schema
from bs4 import BeautifulSoup as bs


class TestReview(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		fname = './scraping/tests/test_files/review1.html'
		with open(fname, 'r') as f:
			html = f.read()
		soup = bs(html)
		tags = soup.find('div',{'id':'REVIEWS'}).findChildren(recursive=False)
		self.reviews = filter(lambda tag: tag.has_attr('id') and 'review_' in tag['id'], tags)

	def test_no_UID(self):
		muacaves = './scraping/bin/tests/mua_caves.html'
		with open(muacaves, 'r') as f:
			html = f.read()
		soup = bs(html)
		tags = soup.find('div',{'id':'REVIEWS'}).findChildren(recursive=False)
		self.reviews = filter(lambda tag: tag.has_attr('id') and 'review_' in tag['id'], tags)
		for item in self.reviews:
			Review(item)
		assert True == True



	def test_rating(self):
		mylist = []
		ratings = [5, 5, 5, 5, 4, 3, 5, 5, 5, 5]
		self.attr_tester('rating', ratings)

	def test_reviewDate(self):
		review_dates = [u'April 27, 2014', 
		u'April 27, 2014', 
		u'April 27, 2014', 
		u'April 27, 2014',
		u'April 27, 2014',
		u'April 27, 2014',
		u'April 27, 2014',
		u'April 26, 2014',
		u'April 26, 2014',
		u'April 26, 2014']
		self.attr_tester('review_date', review_dates)

	def test_uid(self):
		uids = ['BCA2E03421FA88E24B7751A4F385367D',
		'66F6B7D22454BBF97B2C69ADD0267811',
		'989789894816913DA443F65C5798142D',
		'E920711A89AECB97720D1BB9987EA82C',
		'5B696155DD12B0F8B7A3E25EC3332341',
		'220FCBA187778434230BA258E94DE337',
		'23A9C01A7A5EE5B0B7A98FCFAF876B80',
		'1E702CAB93F72B8125DA0FB55572E380',
		'E4DE75931EF108B72CF6BCFDF6A11E57',
		'647AFA5C043DBB3F21555C750F0A31DC']
		self.attr_tester('uid', uids)

	def attr_tester(self, key, ref):
		mylist = []
		for item in self.reviews:
			mylist.append( Review(item).attr[key] )
		assert mylist == ref

	def test_bad_update(self):
		attrs = {'adsf':'New Delhi', 'fdsa':'Nepal'}
		item = self.reviews[0]
		new_review = Review(item, new_attr=attrs)
		for k, v in attrs.items():
			assert k not in new_review.attr.keys()

	def test_legit_update(self):
		parent_attr = ['country', 'item_reviewed', 'type', 'parent_group', 'location']
		attrs = dict(zip(parent_attr, ['null'] * len(parent_attr) ))
		item = self.reviews[0]
		new_review = Review(item, new_attr=attrs)
		for k, v in attrs.items():
			assert k in new_review.attr.keys()



class TestReviewList(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		fname = './scraping/tests/test_files/review1.html'
		with open(fname, 'r') as f:
			html = f.read()
		soup = bs(html)
		tags = soup.find('div',{'id':'REVIEWS'}).findChildren(recursive=False)
		self.reviews = filter(lambda tag: tag.has_attr('id') and 'review_' in tag['id'], tags)

	def setUp(self):
		self.review_list = ReviewList('test.db', vietnam_schema, 'vietnam')
		for item in self.reviews:
			self.review_list.append(Review(item))

	def test_size(self):
		assert len( self.review_list.reviews ) == self.review_list.size()

	def test_dbdump_rating(self):
		self.review_list.DBdump()
		qry = "SELECT COUNT(*) FROM vietnam"
		with sqlite3.connect(self.review_list.dbname) as conn:
			qry = "SELECT rating FROM vietnam"
			cur = conn.cursor()
			cur.execute(qry)
			result = cur.fetchall()
		ratings = map(lambda x: x[0], result)
		assert ratings == [5, 5, 5, 5, 4, 3, 5, 5, 5, 5]

	def test_dbdump_len(self):
		self.review_list.DBdump()
		with sqlite3.connect(self.review_list.dbname) as conn:
			qry = "SELECT COUNT(*) FROM vietnam"
			cur = conn.cursor()
			cur.execute(qry)
			result = cur.fetchall()
		assert result[0][0] == 10

	def tearDown(self):
		pass
		if os.path.isfile(self.review_list.dbname):
			os.remove(self.review_list.dbname)