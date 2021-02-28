Selenium Browser 

Browser class is an interface to semi-safely use Selnium webdriver

* Warning * Any Selnium object returned has a pointer to its parent object, i.e. the webdriver that instantiated it

So, it falls to the calling code to safely handle the object and abstract it so the pointer is safely used / not used

Getting started in the python console

__
>>> From Browser import Browser

>>> b = Browser("/path/to/geckodriver")

>>> b.usage()

>>> dir(b)

>>> help(Browser)
>>> 
__

The Website class is an abstract class to build unique objects that represent a Website

HackerOne_Scrape is just a really good example of everything you should NOT do, but can possibly learn From

CartoonScrape is just a fun little side project. Please be gentle to the servers if you choose to play with it.

TODO: Build a logger class and implement it within Browser

TODO: Build our supplemental BeautifulSoup parsing functions within the Browser class
