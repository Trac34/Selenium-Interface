
from os import getcwd
from os.path import isfile, isdir
from requests import get # instead of relying on caller to supply source code, this class can get it
## TODO: Secure pop operations from reading passed the array length
## TODO: Add security to list reads to ensure array is not empty
## TODO: Check data that is being appended to the internal arrays
class Website:
    """ 
    Abstract Class to use as an interface for building unique website Classes 
    Blame python for the function naming conventions being shitty. Would have been nice to overload the function definitions like in C++....oh well
    Pointer could be given to Parser to fill in the lists ? 
    """
    def __init__(self, url):
         
        self.base_url = url # Extra  dependencies - boo, I know. Comment it out and do it another way if you'd like
        self.urls = []
        self.xPaths = []
        self.ids = []
        self.names = []
        self.tags = []
        self.source = get(self.base_url).content # No javascript here, just a reminder 
## Setters / Getters ## 
    def site(self):
        return self.base_url
    def URL(self, url):
        """ Append url to urls list """
        self.urls.append(url)
    def gURL(self):
        """ LIFO url return """
        return self.urls.pop()
    
    def xPath(self, x):
        """ Append xpath to xPaths list """
        self.xPaths.append(x)
    def gxPath(self):
        """ LIFO return xpath """
        return self.xPaths.pop()

    def ID(self, id):
        """ Append to ids list """
        self.ids.append(id)
    def gID(self):
        """ LIFO return id """
        return self.ids.pop()

    def Name(self, name):
        """ Append to names list """
        self.names.append(name)
    def gName(self):
        """ LIFO return name """
        return self.names.pop()

    def Tag(self, tag):
        """ Append to tags list """
        self.tags.append(tag)
    def gTag(self):
        """ LIFO return tag """
        return self.tags.pop()

    def gFile(self, link, path=getcwd()):
        """ Download file from given link and save it ( Default path is working directory ) """
        if isdir(path):
            name = link.split("/")[-1]
            path += "/{}".format(name)
        try:
            with open(path, "wb") as f:
                print("Saving {} from {}\n".format(path, link))
                f.write( get(link).content )
        except Exception as e:
            print("Unable to GET file from {}\n{}".format(link, e))

    def setSource(self, seleniumBrowser):
        """ Set the source code to the current page the browser is on """
        self.source = seleniumBrowser.viewSource()
    def viewSource(self):
        """ Return website source code """
        return self.source
##  ##
