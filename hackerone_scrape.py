from Browser import Browser
from Browser import bcolors
from time import sleep

class HackerOne:
	## HackerOne Xpaths and configs 
	def __init__(self, browser):
		self.browser = browser
		self.vuln_title_xpath = "//div/div[1]/a/strong"
		self.hacker_xpath = "//div[1]/span/strong/a"
		self.company_xpath = "//div[2]/span/strong/a"
		self.status_xpath = "//li[2]/div/span[2]"
		self.risk_xpath = "//li[3]/div/div[2]"
		self.pay_xpath = "//div/ul/li[4]/strong"
		self.urls = "https://hackerone.com/hacktivity".split() # When multiple urls get added, easier to manage

	def vulnXpath(self):
		return self.vuln_title_xpath
	def hackerXpath(self):
		return self.hacker_xpath
	def companyXpath(self):
		return self.company_xpath
	def statusXpath(self):
		return self.status_xpath
	def riskXpath(self):
		return self.risk_xpath
	def payXpath(self):
		return self.pay_xpath
	def getURLs(self):
		return self.urls

def main():
	b = Browser("/Volumes/Shadowmere/Drivers/geckodriver", False)
	h1 = HackerOne(b)
	b.get(h1.getURLs()[0])
	sleep(8)
	vulns = b.find_xpaths( h1.vulnXpath() )
	hackers = b.find_xpaths( h1.hackerXpath() ) 
	comapnies = b.find_xpaths( h1.companyXpath() )
	statuses = b.find_xpaths( h1.statusXpath() )
	risks = b.find_xpaths( h1.riskXpath() )
	#pays = b.find_xpaths(h1.pay_xpath) # Not 1:1 , sometimes does not exist.
	## Need user defined break point. Stop point to let user choose element || automatically click into elements and grab data behind them
	## Browser needs functions to deal with iFrames
	## Seperate Parser class using BeautifulSoup could be used on Browser.viewSource()
	## What cant be easily grabbed with Selenium we can probably grab with Parser
	data = []
	try:	
		for i,v in enumerate(vulns):
			line = v.text.strip("\n")
			line += "\n\tDiscovered by {} ".format(hackers[i].text.strip("\n"))
			line += "for Company {} ".format(comapnies[i].text.strip("\n"))
			line += "\n\tVulnerability Status: {} ".format(statuses[i].text.strip("\n"))
			line += "\n\tRisk Rating: {} \n__________________".format(risks[i].text.strip("\n"))
			data.append(line)
	except Exception as e:
		print("Failed to fully parse data\n{}".format(e))


	b.quit()

if __name__ == "__main__":
	main()
	
