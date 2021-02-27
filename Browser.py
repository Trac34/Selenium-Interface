from bs4 import BeautifulSoup as bs # External Dependency
from os import getpid
from psutil import process_iter # External dependency 
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from time import sleep


## How to maintain a list of bug bounty URLs ?
# instantiated within Browser class || getter / setter functions ?

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
class Browser:
	"""
Wrapper class to use Selenium as a headless Browser
Requires path to geckodriver. Default second boolean argument headless=True. # can be changed if geckodriver is in PATH
Meant as a semi-secure interface for Selenium browsing, however each selenium object has a pointer to its 'parent', i.e. the driver object
So the class does not prevent the use of webdriver functions directly, but rather is a simple mechanism to be used as a building block.  
	Not to mention that anything with a handle to the class can acess all data members directly...
	Most of this code is based on lessons found here : https://www.geeksforgeeks.org/selenium-python-tutorial/
	"""
	def __init__(self, driver_path, headless=True):
		try:
			assert(type(driver_path)) == str ## Sanity-Check path is a string
			self.options = Options()
			self.options.headless = headless
			self.pid = getpid()		# Useful | Not Useful ? Maybe. 
			self.driver = webdriver.Firefox(options=self.options, executable_path=driver_path)
			self.rootWindowHandle = self.driver.current_window_handle # The handle to the whole browser frame / window
			#If there is a pop-up, we need to switch window handles, but need to be able to go back to the root
			self.expectedChildren = "geckodriver firefox-bin".split()
			self.pids = [] # Instantiating webdriver is a blocking call. Children should be running.
			self.setChildPIDs()
			self.bsource = bs    # create BeautifulSoup Object to set type
		except Exception as e:
			print("[!!] Unable to initialize Browser Class [!!]\n\n{}".format(e))
			exit(1)
		print(f"{bcolors.HEADER}[+] Successfully Instantiated Browser Class{bcolors.ENDC}")
		print(f"{bcolors.OKGREEN}[+] Headless{bcolors.ENDC} firefox now running...") if headless else print("[+] Firefox now running...")
		print(f"[*] Please call {bcolors.OKCYAN}Browser.usage(){bcolors.ENDC} for help. Otherwise dir(Browser) and help(Browser) will also work.\n")
		print(f"{bcolors.HEADER}[+]{bcolors.ENDC} Current Process ID [{bcolors.HEADER} %d {bcolors.ENDC}]" % self.pid)
		for pid in self.pids:
			print(f"\t\t{bcolors.OKGREEN}[+]{bcolors.ENDC} Child Process ID [ {bcolors.OKGREEN} %d {bcolors.ENDC} ]" % pid)

	def usage(self): ## TODO: Need to update once class is finalized
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.get( url ){bcolors.ENDC} will move the browser to the requested page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getTitle(){bcolors.ENDC} will return the title of the current page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getURL(){bcolors.ENDC} will get the URL of the current page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.back(){bcolors.ENDC} will move the browser back one page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.forward(){bcolors.ENDC} will move the browser forward one cached page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.refresh(){bcolors.ENDC} will move the browser forward one cached page")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.find_tags( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_tag( query ){bcolors.ENDC} will search the DOM for all matched ids or the first matched id - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.find_ids( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_id( query ){bcolors.ENDC} will search the DOM for all matched ids or the first matched id - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.find_names( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_name( query ){bcolors.ENDC} will search the DOM for all matched names or the first matched name -{bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.find_xpaths( query ){bcolors.ENDC} and {bcolors.BOLD}{bcolors.OKCYAN}Browser.find_xpath( query ){bcolors.ENDC} will search the DOM for all matched xpaths or the first matched xpath - {bcolors.OKGREEN}returns Selenium Object{bcolors.ENDC}")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.click( element ){bcolors.ENDC} will click on the element passed to it\n\te.g. Browser.click( Browser.find_id('search_bar') )")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.send_keys( element, query ){bcolors.ENDC} will send the query string to the given element.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.scrollBottom(){bcolors.ENDC} executes a javascript line to scroll to the bottom of the page. Useful for 'infinite' dynamically loading pages")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.viewSource(){bcolors.ENDC} returns the current page's source code.")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.getActionObject(){bcolors.ENDC} returns a selenium ActionChain Object so that complex actions can be performed on the DOM.")
		print("Example : action = Browser.getActionObject()")
		print("\taction.key_down(Keys.CONTROL).send_keys('F').key_up(Keys.CONTROL).perform() # CTRL-F # Brings up search bar")
		print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}Browser.quit(){bcolors.ENDC} will close the browser")


	## BEGIN Navigation ##
	def get(self, url):
		""" GET url. Browser will request given URL and run any javascript loaded 
		Loads source code into self.bsource with every successful GET request
		"""
		try:
			assert(type(url)) == str
			self.driver.get(url)
			self.bsource = bs( self.viewSource(), "html.parser" ) # Update internal BeautifulSoup source
		except:
			print("[*] Unable to GET page {}\n".format(url))
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
		if h is not None:
			for handle in handles:
				if handle == h:
					self.driver.switch_to_window( handle )

		if len(handles) > 1:
			print(f"{bcolors.WARNING}[*] More than 2 windows open{bcolors.ENDC}")
			for h in handles:
				print("Handle: {}".format(h))
		
		window = handles[0] # Hardcoded default first in list
		self.driver.switch_to_window( window )
	## END CycleWindow ##

	
	def movetoElement(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.getActionObject().move_to_element(element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[!] Unable to move cursor to given element{bcolors.ENDC}\n")
			print("{}".format(e))
			return -1

	def moveOffset(self,x,y):
		""" Moves cursor to x|y relative to current position"""
		try:
			assert(type(x)) == int
			assert(type(y)) == int
			self.getActionObject().move_by_offset(x,y).perform()
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
			self.getActionObject().click()
		except Exception as e:
			print(f"{bcolors.FAIL}[!!]Unable to click!\n")
			print("{}".format(e))
			return -1

	def contextClick(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.getActionObject().context_click(on_element=element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[*] Failed to context click on given element\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1

	def clickHold(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.getActionObject().click_and_hold(on_element=element).perform()
		except Exception as e:
			print(f"{bcolors.FAIL}[*] Unable to click and hold on given element\n{bcolors.ENDC}")
			print("{}".format(e))
			return -1

	def doubleClick(self, element):
		try:
			assert(type(element)) == webdriver.firefox.webelement.FirefoxWebElement
			self.getActionObject().double_click(on_element=element)
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
			self.getActionObject().send_keys(query).perform() # Send keys to currently focused element
		except Exception as e:
			print("Unable to send_keys to element\n{}".format(e))
			return -1

	def scrollBottom(self):
		""" Execute javascript command to scroll to bottom of the page """
		self.driver.execute_script("window.scroll(0, document.body.scrollHeight)")
	## END Navigation ##

	## BEGIN DOM ##
	def getTitle(self):
		""" Return the title of the current page """
		return self.driver.title


	def getURL(self):
		""" Return current URL """
		return self.driver.current_url


	def findTag(self, query):
		""" Find an element by tag name, e.g. 'h2', 'form', etc.. - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_tag_name(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1

    
	def findTags(self, query):
		""" Find elements by tag name - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_tag_name(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1
			
			
	def findIds(self, query):							## Multiple Elements
		""" Find Elements by ID - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_id(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1
			
			
	def findId(self, query):							## Single Element
		""" Find Element by ID - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_id(query)
		except Exception as e:
			print("Could not find ID: {}\n\n{}".format(query, e))
			return -1

	def findNames(self, query):							## Multiple Elements
		""" Find Elements by Name - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_name(query)
		except Exception as e:
			print("Unable to find name {}\n\n{}".format(query, e))
			return -1

	def findName(self, query):							## Single Element
		""" Find Element by Name - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_name(query)
		except Exception as e:
			print("Unable to find name {}\n\n{}".format(query, e))
			return -1

	def findXpaths(self, query):							## Multiple Elements
		""" Find Elements by Xpath - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_xpath(query)
		except Exception as e:
			print("Unable to find xpath {}\n\n{}".format(query, e))
			return -1

	def findXpath(self, query):							## Single Element
		""" Find Element by Xpath - Returns Selenium Object"""
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_xpath(query)
		except Exception as e:
			print("Unable to find xpath {}\n\n{}".format(query, e))
			return -1

	def findClass(self, name):
		""" Find first class matching name """
		try:
			assert(type(name)) == str
			return self.driver.find_element_by_class_name(name)
		except Exception as e:
			print("[*] Unable to locate class name {}\n{}".format(name, e))
			return -1

	def findClasses(self, name):
		""" Find all classes matching name """
		try:
			assert(type(name)) == str
			return self.driver.find_elements_by_class_name(name)
		except Exception as e:
			print("[*] Unable to locate class name {}\n{}".format(name, e))
			return -1


	def findCSS(self, query):
		""" Find first CSS id matching query """
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_css_selector(query)
		except Exception as e:
			print("[*] Unable to locate CSS id {}\n{}".format(query, e))
			return -1

	def findCSSids(self, query):
		""" Find all CSS ids matching query """
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_css_selector(query)
		except Exception as e:
			print("[*] Unable to locate CSS id {}\n{}".format(query, e))
			return -1

	def findLink(self, query):
		""" Find first link matching query """
		try:
			assert(type(query)) == str
			return self.driver.find_element_by_partial_link_text(query)
		except Exception as e:
			print("[*] Unable to find link by searching {}\n{}".format(query, e))
			return -1

	def findLinks(self, query):
		""" Find all links matching query """
		try:
			assert(type(query)) == str
			return self.driver.find_elements_by_partial_link_text(query)
		except Exception as e:
			print("[*] Unable to find link by searching {}\n{}".format(query, e))
			return -1


	def viewSource(self):
		""" Return the current page's source code """
		return self.driver.page_source
	## END DOM ##

	## BEGIN Browser Control ##
	def getActionObject(self):
		""" Return Selenium ActionChain Object so that complex actions can be performed """
		# Example : action.key_down(Keys.CONTROL).send_keys('F').key_up(Keys.CONTROL).perform() # CTRL-F # Brings up search bar
		return ActionChains(self.driver)


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

				

	def getChildPIDs(self):
		""" Update internal pids list of children """
		return self.pids

	def setChildPIDs(self):
		""" Loop over running processes and compare to expexted children\
			if match and parent is python, update internal class self.pids list
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
		except Exception as e:
			print(f"{bcolors.WARNING}[!] Unable to Stop process [!]{bcolors.ENDC}")
			print("{}".format(e))
			exit(-1)
		print(f"{bcolors.HEADER}[-] Firefox Process Stopped{bcolors.ENDC}")
	## End Browser Control ##