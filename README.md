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

TODO: Build out the Website class

TODO: Build a logger class and implement it within Browser

TODO: Build out supplemental BeautifulSoup parsing functions within the Browser class

TODO: Build Main Script to take both Browser and Website classes as args and uses them to scrape the site(s), writing the results to a file and/or returning them

TODO: Define method for storing hacker names, company names, Weakness Types, Bounty, Date, Severity, and Visibility - so that we might scrape and search the site solely based on these defined attributes, i.e. we only care about these companies with specific severity levels

The goal I have in mind is to reduce the complexity to simply `Scrape( Browser, Website )`, where the website object would contain the desired attributes and their locations.  
The Browser class holds all of the navigational and scraping methods.
Scrape acts as a controller and establishes an order to the scrape as well as handling the returned data.
___________________________________________________________________________________________________________________________________________________________

Automating False-Positive Work-flow.
We need to update the Qualys record to avoid VULs / VITs being re-created after closure from our False Positive Workflow.

Stop-Gap until we can get this integrated into SN / javascript .
High-Level Steps:
1.       Feed the script a False Positive record #
2.       Search related records for hostname, IP, QID within Service-Now
3.       Login into Qualys
4.       Search for the asset and ensure match
5.       Open Host Record in Qualys
6.       Search for specific QID(s)
7.       Close the vulnerability && Save the record
8.       Update the SN record && Save
