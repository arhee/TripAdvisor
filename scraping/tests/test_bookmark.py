import unittest
import os
import os.path

from ..bin.bookmark import Bookmark

class testDeck(unittest.TestCase):
	def setUp(self):
		self.fname = 'test.txt'
		self.chkpt = Bookmark(self.fname)

	def test_hierarchy(self):
		assert self.chkpt.hierarchy == ['city', 'parent_page', 'review_page', 'group_page']

	def test_file_create(self):
		self.assertTrue( os.path.isfile(self.fname) )

	def test_update(self):
		testdict = {'city':['a','b'], 'parent_page':1, 'review_page':2, 'group_page':3}
		self.chkpt.update(testdict)
		new_chkpt = Bookmark(self.fname)

		for k, v in new_chkpt.bookmarks.items():
			assert testdict[k] == new_chkpt.bookmarks[k]

	def tearDown(self):
		os.remove(self.fname)
