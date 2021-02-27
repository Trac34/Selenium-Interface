from bs4 import BeautifulSoup as bs
import re

class Parser:
    """ Broken Parser Class that uses BeautifulSoup. What is the best way to use BeautifulSoup here?
    Is it necessary to build an interface for BS? Should we just use BS directly in the Browser class?
    Just build certain functions with BS inside Browser...
    We have source in the browser, so make bso as an interal object in the Browser

    Dead Class unless anyone sees a use-case to fix and use 
    """
    def __init__(self, source):
        try:
            assert(type(source)) == str or bytes
            self = bs(source, "html.parser")
            self.pointer = None
        except Exception as e:
            print("[!!] Failed to Instantiate Parser Class.\n{}".format(e))
            
"""
    def feed(self, source):
        self.source = bs(source, 'html.parser')

    def analyze(self):
        #src = self.source
        root = self.source.html
        head = self.source.head
        title = self.source.title.string
        links = self.source.find_all("a") # find_all(name, attrs, recursive, string, limit, **kwargs)

    
    def text(self):
        return self.get_text()
    
    def strings(self):
        for string in self.source.stripped_strings:
            print(repr(string))
    
    def findID(self, query):
        return self.source.find_all(id=query)
    
    def href(self, query):
        return self.source.find_all(re.compile(query))
"""