# get soup
import sqlite3
import schema

class ReviewPage(object):
    def __init__(self, soup, parent_attrs, dbname, url):
        self.soup = soup
        self.attr = {}
        parent_attr = ['country', 'type', 'location']

        if parent_attrs:
            for k, v in parent_attrs.items():
                if k in parent_attr:
                    self.attr[k] = v

        self.tbl_schema = schema.review_schema
        self.dbname = dbname

        self.attr['url'] = url
        self.tbl_name = 'attractions'
        self.attr['choice_award'] = self.get_choice_award()
        self.attr['rank'] = self.get_rank()
        self.attr['coe'] = self.get_coe()
        self.attr['name'] = self.get_name()
        
    def get_choice_award(self):
        if self.soup.find('img',{'alt':'Travelers\' Choice award winner'}):
            return 1
        return 0

    def get_rank(self):
        numstr = [x for x in self.soup.find('b',{'class':'rank_text wrap'}).text if x.isalnum()]
        return int("".join(numstr))

    def get_coe(self):
        if self.soup.find('div',{'class':'coeBadgeDiv'}):
            return 1
        return 0

    def get_name(self):
        return self.soup.find('div',{'class':"heading_name_wrapper"}).text.strip()

    def DBdump(self):
        with sqlite3.connect(self.dbname) as conn:
            cur = conn.cursor()
            cur.execute(self.tbl_schema)            
            qmarks = ', '.join('?' * len(self.attr.keys()))
            qry = "INSERT OR IGNORE INTO {} {} VALUES ({})".format(self.tbl_name, tuple(self.attr.keys()), qmarks)
            cur.execute(qry, self.attr.values()) 
            conn.commit()
            self.attr = {}