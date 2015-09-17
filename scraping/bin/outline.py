## change attraction to something else.  It could be restaurants etc...












Possible classes
- city 
- attraction list

-----hierarchy----------
City -> Attraction list -> reviews (class) of individual attractions

Pass the html to this class which finds the 

class attraction_list(self):
	def __init__(self, html):
		self.soup = bs(html)
		attractions = []
		# get all attractions 

	def get_list(fdsfds):
		dsfdf

import json


-------Checkpoints-------------

def get_remaining(x, mylist):
	try:
		idx = mylist.index(x)
	except:
		idx = 0
	return mylist[idx:]


#Initialize the checkpoints
chkpt = CheckPoint(filename)
start = chkpt.bookmarks


city_list = get_city_list( html )
if start['city_list']:
	city_list = get_remaining(start['city_list'], city_list)
	start['city_list'] = None

for parent_page in city_list:

	if start['parent_page']:
		parent_page = start['parent_page']			
		start['parent_page'] = None

	# Flip throught the attractions in a given city.
	while parent_page:
		# Create a remaining attraction list
		driver.get( parent_page )
		parent_list = get_parent_list( driver.page_source )

		# if there is a review bookmark.  start the crawler with that bookmark
		if start['review_page']:
			review_page = start['review_page']
			start['review_page'] = None

		#make this part more efficient?
		parent_list = get_remaining( get_review_root(review_page), parent_list)


		# go through all the attractions in the list
		for parent in parent_list:
			review_crawler( parent, jsonfile )

		
		parent_page = nextbutton()
		chkpt.update(parent_page = parent_page)

	city_list = city_list[1:]		
	chkpt.update(city_list = city_list)