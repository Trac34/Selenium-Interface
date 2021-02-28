from bs4 import BeautifulSoup as bs # External Dependency
from os import getpid
from os import getcwd
from psutil import process_iter # External dependency 
from re import compile, Pattern
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from time import sleep
import threading # Another External dependency. Just using a thread for a polling function
# Python never actually spins up a concurrent thread. It's just stricter scheduling.
# Not sure how it works for multiprocessing / Process python module


## How to maintain a list of bug bounty URLs -> Website Class to make unqiue website objects 


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Class members can't be protected like in C++. Everything is public.
# Anything with a pointer to the class can access its functions and members
##TODO: Integrate the BeautifulSoup Parser class to supplement functions
##TODO: Create and implement logger class to use instead of print statements
class Browser:
	"""
Wrapper class to use Selenium as a headless Browser
Requires path to geckodriver. Default second boolean argument headless=True. # can be changed if geckodriver is in PATH
3rd parameter is an optional proxy that should be formatted HOST:PORT
Meant as a semi-secure interface for Selenium browsing, however each selenium object has a pointer to its 'parent', i.e. the driver object
So the class does not prevent the use of webdriver functions directly, but rather is a simple mechanism to be used as a building block.  
Not to mention that anything with a handle to the class can acess all data members directly...
	Arguments: Mandatory[ "/path/to/geckodriver" ], Optional[ headless=True, proxy="HOST:PORT", tor=False]
	Most of this code is based on lessons found here : https://www.geeksforgeeks.org/selenium-python-tutorial/
	"""
	def __init__(self, driver_path, headless=True, proxy="", tor=False):
		try:
			assert(type(driver_path)) == str ## Sanity-Check path is a string
			self.handles = []
			self.pids = [] # Instantiating webdriver is a blocking call. Children should be running.
			self.profile = FirefoxProfile()
			self.options = Options()
			self.options.headless = headless
			self.expectedChildren = "geckodriver firefox-bin".split()
			self.pid = getpid()		# Useful | Not Useful ? Maybe.
			if proxy != "": # proxy defined as "HOST:PORT"
				webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
					"httpProxy": proxy,
					"ftpProxy": proxy,
					"sslProxy": proxy,
					"proxyType": "MANUAL",
				}
			if tor: # Set up firefox profile to use tor socks proxy
				self.profile.set_preference('network.proxy.type', 1)
				self.profile.set_preference('network.proxy.socks', '127.0.0.1')
				self.profile.set_preference('network.proxy.socks_port', 9050)
				self.profile.set_preference("network.proxy.socks_remote_dns", False)
				self.profile.update_preferences()
			self.driver = webdriver.Firefox(options=self.options, firefox_profile=self.profile, executable_path=driver_path)
			self.setChildPIDs()
			self.rootWindowHandle = self.driver.current_window_handle # The handle to the whole browser frame / window
			#If there is a pop-up, we need to switch window handles, but need to be able to go back to the root
			self.bsource = bs    # create BeautifulSoup Object to set type
			self.windowChecker = threading.Thread(target=self.startWindowCheck, name="windowChecker") # If another thread has to be used, switch to array of threads as thread-pool
			self.windowChecker.start() # Start thread to poll if there are multiple windows open
			# Helpful for headless browsing when unexpected pop-ups occur
		except Exception as e:
			print("[!!] Unable to initialize Browser Class [!!]\n\n{}".format(e))
			exit(1)
		print(f"{bcolors.HEADER}[+] Successfully Instantiated Browser Class{bcolors.ENDC}")
		print(f"{bcolors.OKGREEN}[+] Headless{bcolors.ENDC} firefox now running...") if headless else print("[+] Firefox now running...")
		print(f"{bcolors.OKGREEN}[+] TOR{bcolors.ENDC} proxy in use...\n") if tor else print("\n")
		print(f"{bcolors.HEADER}[*]{bcolors.ENDC} Please call {bcolors.OKCYAN}Browser.usage(){bcolors.ENDC} for help. Otherwise {bcolors.OKGREEN}dir(Browser){bcolors.ENDC} and {bcolors.OKGREEN}help(Browser){bcolors.ENDC} will also work.")
		print(f"{bcolors.HEADER}[+]{bcolors.ENDC} Current Process ID [{bcolors.HEADER} %d {bcolors.ENDC}]" % self.pid)
		for pid in self.pids:
			print(f"\t\t\t{bcolors.OKGREEN}[+]{bcolors.ENDC} Child Process ID [ {bcolors.OKGREEN} %d {bcolors.ENDC} ]" % pid)

	def usage(self): ## TODO: Need to update once class is finalized
		print(f"\n{bcolors.BOLD}{bcolors.OKGREEN}Browser( path, headless=True, proxy='', tor=False){bcolors.ENDC} Class instatiation.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.get( url ){bcolors.ENDC} will move the browser to the requested page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getTitle(){bcolors.ENDC} will return the title of the current page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getURL(){bcolors.ENDC} will get the URL of the current page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.back(){bcolors.ENDC} will move the browser back one page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.forward(){bcolors.ENDC} will move the browser forward one cached page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.refresh(){bcolors.ENDC} will move the browser forward one cached page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.multipleWindows(){bcolors.ENDC} will return boolean True if multiple windows are open.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.cycleWindow( handle=None ){bcolors.ENDC} will switch windows to handle if passed, otherwise it will switch to first handle it finds.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.movetoElement( element ){bcolors.ENDC} will move cursor to given element.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.moveOffset( x, y ){bcolors.ENDC} will move cursor to given x | y positions relative to current position, i.e. new_x = current_x + x")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.findTags( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_tag( query ){bcolors.ENDC} will search the DOM for all matched ids or the first matched id - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.findIds( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_id( query ){bcolors.ENDC} will search the DOM for all matched ids or the first matched id - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.findNames( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_name( query ){bcolors.ENDC} will search the DOM for all matched names or the first matched name -{bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.findXpaths( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_xpath( query ){bcolors.ENDC} will search the DOM for all matched xpaths or the first matched xpath - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.click( element ){bcolors.ENDC} will click on the element passed to it\n\te.g. Browser.click( Browser.find_id('search_bar') )")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.contextClick( element ){bcolors.ENDC} will right-click on the element passed to it\n\te.g. Browser.contextClick( Browser.find_id('search_bar') )")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.clickHold( element ){bcolors.ENDC} will click and hold on the element passed to it.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.doubleClick( element ){bcolors.ENDC} will double-click on the element passed to it.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.switchFrame( element ){bcolors.ENDC} will switch context to given iFrame element.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.defaultFrame( element ){bcolors.ENDC} will switch context to the root frame.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.sendKeys( element, query ){bcolors.ENDC} will send the query string to the given element.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.scrollBottom(){bcolors.ENDC} executes a javascript line to scroll to the bottom of the page. Useful for 'infinite' dynamically loading pages")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.scrollTop(){bcolors.ENDC} executes a javascript line to scroll to the Top of the current page.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.sreenshot( path=getcwd(), name='screenshot.png', element=None ){bcolors.ENDC} creates a base64 text file under [path] with [name] or take picture of given [element].")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.viewSource(){bcolors.ENDC} returns the current page's source code.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getText(){bcolors.ENDC} returns the all of the current page's text.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.soupSearch( query ){bcolors.ENDC} searches current page source for passed query. Takes string, list, or re.Pattern")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.script( script, args=None ){bcolors.ENDC} executes passed string as javascript in context of current page with [args] to the script as the second argument.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.actionObject(){bcolors.ENDC} returns a selenium ActionChain Object so that complex actions can be performed on the DOM.")
		print("Example : action = Browser.actionObject()")
		print("\taction.key_down(Keys.CONTROL).send_keys('F').key_up(Keys.CONTROL).perform() # CTRL-F # Brings up search bar")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.quit(){bcolors.ENDC} will close the browser")


	### BEGIN Navigation ###
	def get(self, url):
		""" GET url. Browser will request given URL and run any javascript loaded 
		Loads source code into self.bsource with every successful GET request
		"""
		try:
			assert(type(url)) == str
			self.driver.get(url)
			self.bsource = bs( self.viewSource(), "lxml" ) # Update internal BeautifulSoup source
		except Exception as e:
			print("[*] Unable to GET page {}\n{}".format(url, e))
			return -1

	def back(self):
		""" Back One Page """
		self.driver.back()


	def forward(self):
		""" Forward One Page """
		self.driver.forward()
	

	def refresh(self):
		"""Refresh the current page"""
		self.driver.refresh()

	def enter(self):
		""" Send the Enter key """
		self.actionObject().key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

	def multipleWindows(self):
		""" False if only one handle, otherwise True. Polled using thread"""
		return False if (len(self.driver.window_handles) == 1) else True

	def cycleWindow(self, h=None):
		""" Gather Window handles, check passed handle against discovered ( if passed )\
			switch to window if handle is matched otherwise \
			print warning if more than 2 windows open and \
				switch to first handle in list 
		"""
		handles = []
		for handle in self.driver.window_handles:
			if handle != self.rootWindowHandle:
					handles.append(handle)
		self.handles = handles
		if h is not None:
			for handle in handles:
				if handle == h:
					self.driver.switch_to_window( handle )
					return 0

		if len(handles) >= 1:
			print(f"{bcolors.WARNING}[*] More than 2 windows open{bcolors.ENDC}")
			for h in handles:
				print("\t[+] Handle: {}".format(h))
			print("Switching to handle: {}".format(handles[0]))
		
		window = handles[0] # Hardcoded default first in list
		self.driver.switch_to_window( window )
		return 0
	## END CycleWindow ##

	
	def movetoElement(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.actionObject().move_to_element(element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[!] Unable to move cursor to given element{bcolors.ENDC}\n")
			print("{}".format(e))
			return -1

	def moveOffset(self,x,y):
		""" Moves cursor to x|y relative to current position"""
		try:
			assert(type(x)) == int
			assert(type(y)) == int
			self.actionObject().move_by_offset(x,y).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[!] Failed to move cursor.\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1
			

	def click(self, element=None):
		""" Safely Click passed Firefox Element or current cursor location"""
		if element is not None:
			try:
				assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
				element.click()
				return
			except Exception as e:
				print("Unable to click element\n{}".format(e))
				return -1
		try:
			self.actionObject().click()
		except Exception as e:
			print(f"{bcolors.FAIL}[!!]Unable to click!{bcolors.ENDC}\n")
			print("{}".format(e))
			return -1

	def contextClick(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.actionObject().context_click(on_element=element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[*] Failed to context click on given element\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1

	def clickHold(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.actionObject().click_and_hold(on_element=element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[*] Unable to click and hold on given element\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1

	def doubleClick(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.actionObject().double_click(on_element=element)
		except Exception as e:
			print(f"{bcolors.WARNING}[*] Unable to double click on given element\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1

	def switchFrame(self, element):
		""" Safely switch context to iframe Firefox Element """
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			wait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(element))
		except Exception as e:
				print("[*] Unable to switch context to given element\n{}".format(e))
				return -1
	
	def defaultFrame(self):
		""" Set the javascript environment / Browser Frame context to the root of the current page """
		self.driver.switch_to.default_content()

	def sendKeys(self, query, element=None):
		""" Safely send keys to focused || passed element """
		try:
			assert(type(query)) == str
			if element is not None:
				assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
				element.send_keys(query) # Send Keys to element
				return 0
			self.actionObject().send_keys(query).perform() # Send keys to currently focused element
		except Exception as e:
			print("Unable to send_keys to element\n{}".format(e))
			return -1

	def scrollTop(self):
		""" Execute javascript command to scroll to bottom of the page """
		self.driver.execute_script("window.scrollTop(0)")


	def scrollBottom(self):
		""" Execute javascript command to scroll to bottom of the page """
		self.driver.execute_script("window.scroll(0, document.body.scrollHeight)")
	### END Navigation ###

	### BEGIN DOM ###
	def getTitle(self):
		""" Return the title of the current page """
		return self.driver.title


	def getURL(self):
		""" Return current URL """
		return self.driver.current_url


	def findTag(self, query):
		""" Find an element by tag name, e.g. 'h2', 'form', etc.. - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_tag_name(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1

    
	def findTags(self, query):
		""" Find elements by tag name - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_tag_name(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1
			
			
	def findIds(self, query):							## Multiple Elements
		""" Find Elements by ID - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_id(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1
			
			
	def findId(self, query):							## Single Element
		""" Find Element by ID - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_id(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1

	def findNames(self, query):							## Multiple Elements
		""" Find Elements by Name - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_name(query)
		except Exception as e:
			print("Unable to find name {}\n\n{}".format(query, e))
			return -1

	def findName(self, query):							## Single Element
		""" Find Element by Name - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_name(query)
		except Exception as e:
			print("Unable to find name {}\n\n{}".format(query, e))
			return -1

	def findXpaths(self, query):							## Multiple Elements
		""" Find Elements by Xpath - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_xpath(query)
		except Exception as e:
			print("Unable to find xpath {}\n\n{}".format(query, e))
			return -1

	def findXpath(self, query):							## Single Element
		""" Find Element by Xpath - Returns Selenium Object"""
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_xpath(query)
		except Exception as e:
			print("Unable to find xpath {}\n\n{}".format(query, e))
			return -1

	def findClass(self, name):
		""" Find first class matching name """
		try:
			assert(type(name)) == str or Pattern
			return self.driver.find_element_by_class_name(name)
		except Exception as e:
			print("[*] Unable to locate class name {}\n{}".format(name, e))
			return -1

	def findClasses(self, name):
		""" Find all classes matching name """
		try:
			assert(type(name)) == str or Pattern
			return self.driver.find_elements_by_class_name(name)
		except Exception as e:
			print("[*] Unable to locate class name {}\n{}".format(name, e))
			return -1


	def findCSS(self, query):
		""" Find first CSS id matching query """
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_css_selector(query)
		except Exception as e:
			print("[*] Unable to locate CSS id {}\n{}".format(query, e))
			return -1

	def findCSSids(self, query):
		""" Find all CSS ids matching query """
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_css_selector(query)
		except Exception as e:
			print("[*] Unable to locate CSS id {}\n{}".format(query, e))
			return -1

	def findLink(self, query):
		""" Find first link matching query """
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_element_by_partial_link_text(query)
		except Exception as e:
			print("[*] Unable to find link by searching {}\n{}".format(query, e))
			return -1

	def findLinks(self, query):
		""" Find all links matching query """
		try:
			assert(type(query)) == str or Pattern
			return self.driver.find_elements_by_partial_link_text(query)
		except Exception as e:
			print("[*] Unable to find link by searching {}\n{}".format(query, e))
			return -1

	def getLinks(self):
		""" Return all links on current page """
		hrefs = []
		for link in self.bsource.find_all('a'):
			hrefs.append(link.get('href'))
		return hrefs

	def getText(self):
		""" Wrapper around BeautifulSoup get_text function """
		return self.bsource.get_text() # "no value for 'self' in unbound method call" pylint error. Still runs. Idk. 

	def soupSearch(self, query):
		""" Function that accepts a string, list, or regex Pattern to use to search the source code of the current page """
		try:
			assert(type(query)) == str or list or Pattern
			return self.bsource.find_all(query)
		except Exception as e:
			print(f"{bcolors.FAIL}[!][!]{bcolors.ENDC} Unable search source using BeautifulSoup.\n")
			print("{}".format(e))
			return -1

	def viewSource(self):
		""" Return the current page's source code """
		return self.driver.page_source
	### END DOM ###

	## BEGIN Browser Control ##
	def actionObject(self):
		""" Return Selenium ActionChain Object so that complex actions can be performed """
		# Example : action.key_down(Keys.CONTROL).send_keys('F').key_up(Keys.CONTROL).perform() # CTRL-F # Brings up search bar
		return ActionChains(self.driver)

	def setUA(self, useragent):
		""" Non-functional. Setting the useragent requires a Browser restart. Need to define that process."""
		pass

	def getUA(self):
		""" Execute javascript to get current userAgent string """
		self.script("return navigator.userAgent")

	def checkIP(self):
		""" Checks ifconfig.me for external IP address """
		self.get("https://ifconfig.me/")
		return self.findId("ip_address").text


	def screenshot(self, path=getcwd(), name="screenshot.png", element=None):
		""" Takes a screenshot of the current page and save it in path ( Default working directory )."""
		p = path +"/"+name
		if element is not None:
			try:
				assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
				element.save_screenshot(p)
				return 0
			except Exception as e:
				print("Unable to save screenshot using given element\n{}".format(e))
				return -1
		self.driver.save_screenshot(p)
		return 0


	def getCookies(self):
		""" Return all cookies """
		try:
			return self.driver.get_cookies()
		except Exception as e:
			print(f"{bcolors.FAIL}[*] Unable to get cookies{bcolors.ENDC}")
			print("{}".format(e))
			return -1


	def getCookie(self, name):
		""" Return specified cookie """
		try:
			return self.driver.get_cookie(name)
		except Exception as e:
			print("Could not find cookie {}\n{}".format(name,e))
			return -1

	def addCookie(self, cookie):
		"""Cookie should be ('name' : 'foo', 'otro' : 'aqui'), i.e. tuple of dicts, and adds to browser """
		try:
			self.driver.add_cookie(cookie)
		except Exception as e:
			print("[*] Unable to add specified cookie: {}\n{}".format(cookie,e))
			return -1


	def delCookie(self, name):
		try:
			self.driver.delete_cookie(name)
		except Exception as e:
			print("Unable to delete specified cookie: {}\n{}".format(name, e))
			return -1

	
	def delCookies(self):
		try:
			self.driver.delete_all_cookies()
		except Exception as e:
			print(f"{bcolors.WARNING}[!!] Unable to delete cookies!\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1


	def script(self, javascript, args=None):
		try:
			if args is not None:
				assert(type(args)) == list
				self.driver.execute_script(javascript, args)
				return 0
			self.driver.execute_script(javascript)
		except Exception as e:
			print(f"{bcolors.FAIL}[-]{bcolors.ENDC} Unable to execute javascript")
			print("{}".format(e))
			return -1


	def startWindowCheck(self):
		""" Infinite while loop to be used by thread to check for multiple windows open"""
		try:
			assert( type( threading.current_thread() ) ) == threading.Thread
			print(f"\n{bcolors.OKCYAN}[+]{bcolors.ENDC}Thread \'%s\' created with PID: %d" % ( threading.current_thread().name, getpid() ))
		except Exception as e:
			print(f"{bcolors.FAIL}[!]{bcolors.ENDC}Unable to run startWindowCheck function.\n")
			print("{}".format(e))
			return -1
		try:
			while True:
				if self.multipleWindows():
					print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Multiple Windows open.\n")
					self.handles = self.driver.window_handles
					for h in self.handles:
						print("\t[+] Handle : {}".format(h))
					sleep(30) # Need a better way to wait / wake thread
				else:
					sleep(10)
		except Exception as e:
			print(f"{bcolors.OKGREEN}[-]{bcolors.ENDC} WindowChecker thread returning.\n")
			return 1
		except KeyboardInterrupt:
			print(f"{bcolors.OKGREEN}[-]{bcolors.ENDC} WindowChecker thread returning.\n")
			return 2		

	def getChildPIDs(self):
		""" Update internal pids list of children """
		return self.pids

	def setChildPIDs(self):
		""" Loop over running processes and compare to expected children\
			if match and parent is python, update internal self.pids list
		"""
		pids = []
		for proc in process_iter():
			for child in self.expectedChildren:
				if child == proc.name():
					if proc.parent().name() == "Python": # Hardcoded string comparison. Sue me.
						pids.append(proc.pid)
		self.pids = pids


	def quit(self):
		self.driver.close() # Close the current page
		print(f"{bcolors.OKGREEN}Browser Closing{bcolors.ENDC}...\n")
		try:
			self.driver.quit() # Stop the process
			self.windowChecker.join() # Wait for thread
		except Exception as e:
			print(f"{bcolors.WARNING}[!] Unable to Stop process [!]{bcolors.ENDC}")
			print("{}".format(e))
			self.windowChecker.join() # Wait for thread
			#exit(-1)
		print(f"{bcolors.HEADER}[-] Firefox Process Stopped{bcolors.ENDC}")
		#exit(0)
	## End Browser Control ##