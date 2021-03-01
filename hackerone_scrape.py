from bs4 import BeautifulSoup as bs
from Browser import Browser
from Browser import bcolors
from time import sleep
from Website import Website

#Deleted everything and put new garbage in here :) 

## to be used by BeautifulSoup / Selenium to pull links and text 
# Text data, after the javascript has loaded, can be pulled with BeautifulSoup
# links can be passed from BeautifulSoup to Selenium for navigation and to load javascript
h1_magic_classes = ["daisy-link ahref daisy-link hacktivity-item__publicly-disclosed spec-hacktivity-item-title"]
def main():
	b = Browser("/Volumes/Shadowmere/Drivers/geckodriver", False)
	#b.get("https://hackerone.com/hacktivity")
	#print("Got page")
	#hackerone_hacktivity_linkscrape( b.bsource )
	#print("Done Scraping")
	b.usage()
	b.quit()

# Saved loop from console that shows disclosed vulns and links to details on https://hackerone.com/hacktivity
def hackerone_hacktivity_linkscrape(bso):
	print("Scraping page")
	for a in bso('a', {'class':'daisy-link ahref daisy-link hacktivity-item__publicly-disclosed spec-hacktivity-item-title'}):
		print("{}\n{}\n".format(a.text, a['href']))
		#Save / Print Title
		# browser.get(link)
		# parse report for state, disclosed, reported to, reported at, asset, CVE-ID, weakness, bounty, severity, paricipants, visibility using BeautifulSoup
		# Then check if there is a summary by the company
		# Read timeline and look for keywords "Summary", "Steps to Reproduce", and "Impact", get all text in between those headers
		# Check for attachments in the timeline such as [.png], [.mp4], [.jpg]
		# Create directory based on Company Name, move into it, pass attachment links to Website.gFile( link ) to download file
		# Scroll to top of page and take screenshot, Scroll to "Timeline" and take another screenshot - Just to have for manual review if need be.

if __name__ == "__main__":
	main()
	
