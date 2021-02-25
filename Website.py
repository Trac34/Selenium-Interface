
## TODO: Secure pop operations from reading passed the array length
## TODO: Add security to list reads to ensure array is not empty
## TODO: Check data that is being appended to the internal arrays
class Website:
    """ 
    Abstract Class to use as an interface for building unique website Classes 
    Blame python for the function naming conventions being shitty. Would have been nice to overload the function definitions like in C++....oh well
    """
    def __init__(self, url):
        self.base_url = url
        self.urls = []
        self.xPaths = []
        self.ids = []
        self.names = []
        self.tags = []

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
