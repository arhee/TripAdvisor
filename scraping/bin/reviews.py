from bs4 import BeautifulSoup as bs
import sqlite3

class Review(object):
    """
    This class receives BeautifulSoup data and extracts relevant TripAdvisor 
    review data. It can also receive additional properties (current) that is
    not included in the html data.
    """
    def __init__(self, soup, new_attr=None):
        self.soup = soup
        self.attr = {}

        parent_attr = ['country', 'item_reviewed', 'type', 'parent_group', 'location', 'item_url']

        if new_attr:
            for k, v in new_attr.items():
                if k in parent_attr:
                    self.attr[k] = v
                
        self.attr['rating'] = self.get_rating()
        self.attr['review'] = self.get_review()
        self.attr['review_date'] = self.get_reviewdate()
        self.attr['visit_date'] = self.get_visitdate()
        self.attr['title'] = self.get_title()
        self.attr['uid'] = self.get_uid()
        self.attr['reviewID'] = self.get_reviewID()
        self.attr['user'] = self.get_user()
        self.attr['user_home'] = self.get_userhome()
        self.attr['key'] = self.attr['uid'] + '-' + str(self.attr['reviewID']) 
        
    def get_rating(self):        
        tag = self.soup.find(lambda tag: tag.name == 'img' and tag.has_attr('alt') and 'stars' in tag['alt'])
        return int(tag['alt'][0])
    
    def get_review(self):
        texts = self.soup.findAll('div',{'class':'entry'})
        return texts[-1].text.strip()
    
    def get_reviewdate(self):
        txt = self.soup.find("span", {"class":"ratingDate"}).contents[0]
        date = txt.replace('Reviewed','').strip()
        return date #date_object.strftime('%m-%d-%Y')

    def get_visitdate(self):
        try:
            txt = self.soup.find('div',{'class':'recommend'}).text.strip()
        except AttributeError:
            txt = ''
        return txt.replace('Visited','').strip()
    
    def get_title(self):
        return self.soup.find('span',{'class':'noQuotes'}).text.strip()
    
    def get_uid(self):
        try:
            tag = self.soup.find('div',{'class':'member_info'})
            uid = tag.find(lambda tag: tag.name=='div' and tag.has_attr('id'))['id']
            return uid[4:uid.find('-')].strip()
        except TypeError:
            return ''
    
    def get_reviewID(self):
        return int(self.soup['id'][7:])

    def get_user(self):
        try:
            return self.soup.find('div',{'class':'username mo'}).text.strip()
        except AttributeError:
            return ''    
        
    def get_userhome(self):
        try:
            return self.soup.find('div',{'class':'location'}).text.strip()
        except AttributeError:
            return ''
    
    def get_vars(self):
        return self.attr.keys()
    
    def get_values(self):
        return self.attr.values()
    

class ReviewList(object):
    """
    This class holds all the Review objects and can insert them into a sqlite3 database
    """
    
    def __init__(self, dbname, tbl_schema, tbl_name):
        self.reviews = []
        self.dbname = dbname
        self.tbl_schema = tbl_schema
        self.tbl_name = tbl_name
        self.dumpsize = 3
        
    def size(self):
        return len(self.reviews)
    
    def DBdump(self):
        if len(self.reviews) == 0:
            return

        with sqlite3.connect(self.dbname) as conn:
            cur = conn.cursor()
            cur.execute(self.tbl_schema)
            for item in self.reviews:
                qmarks = ', '.join('?' * len(item.get_vars()))
                qry = "INSERT OR IGNORE INTO {} {} VALUES ({})".format(self.tbl_name, tuple(item.get_vars()), qmarks)
                cur.execute(qry, item.get_values()) 
            conn.commit()
        self.reviews = []
    
    def funct_test(self):
        return len(self.reviews)

    def append(self, item):
        self.reviews.append(item)

        if self.size() >= self.dumpsize:
            self.DBdump()

        