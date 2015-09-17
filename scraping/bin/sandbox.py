import crawlers
from reviews import Review, ReviewList
from bs4 import BeautifulSoup as bs
from schema import vietnam_schema


with open('tests/mua_caves.html') as f:
	lines = f.read()

soup = bs(lines)

def listfct(soup):        
    tags = soup.find('div',{'id':'REVIEWS'}).findChildren(recursive=False)
    reviews = filter(lambda tag: tag.has_attr('id') and 'review_' in tag['id'], tags)
    return reviews

mylist = listfct(soup)


myReviewList = ReviewList('sandbox.db', vietnam_schema, 'vietnam')

for item in mylist:
	myReviewList.append(Review(item))






"""
for ix, item in enumerate(mylist):
	print ix
	Review(item)
"""