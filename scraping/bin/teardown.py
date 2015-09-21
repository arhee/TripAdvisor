import os
import os.path
if os.path.isfile('bookmark.json'):
	os.remove('bookmark.json')
if os.path.isfile('test.db'):
	os.remove('trip_advisor.db')