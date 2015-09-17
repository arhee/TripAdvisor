import json

class Bookmark:
    """
    Saves the current page
    """
    def __init__(self, fname):
        self.fname = fname
        self.hierarchy = ['city', 'parent_page', 'review_page', 'group_page']
        self.bookmarks = {}
        self._loadfile()

    def _loadfile(self):
        try:
            with open(self.fname, 'r') as f:
                data = json.load(f)
                for k,v in data.items():
                    if k in self.hierarchy:
                        self.bookmarks[k] = v
        except:
            open(self.fname, 'w').close()
            
    def _savefile(self):
        with open(self.fname, 'w') as f:
            json.dump(self.bookmarks ,f)
            
    def update(self, update_dict):
        for k, v in update_dict.items():
            if k in self.hierarchy:
                self.bookmarks[k] = v
            else:
                raise KeyError('Passed keyword is not a bookmark')
        self._savefile()
