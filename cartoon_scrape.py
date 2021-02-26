from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from time import sleep

def main():
	"""
Simple Selenium script to scrape Anime or Cartoons from 'watchcartoononline.io'
Issues finding video player on DOM due to Iframe usage. 
Final steps to mute, change to HD ( if available ) and then download are missing
	"""	
	driver_path = "/Volumes/Shadowmere/Drivers/geckodriver"

	url = "https://watchcartoononline.io/"
	search_xpath = "/html/body/div/table/tbody/tr/td[2]/table/tbody/tr[3]/td/div[2]/form/input"
	
	driver = webdriver.Firefox(executable_path=driver_path)
	driver.get(url)

	search = driver.find_element_by_xpath(search_xpath)
	search.click()
	
	query = input("Search Anime or Cartoon: ")
	search.send_keys(query)
	search.submit()
	
	print("Waiting for page to load...\n")
	sleep(5)
	result = driver.find_element_by_link_text(query)
	result.click()

	result = '' # Invalid pointer once result is clicked, so just clear it out

	ep_xpath = '//*[@id="catlist-listview"]//a' # All the links in the episode list
	links = driver.find_elements_by_xpath(ep_xpath)

	links.reverse() # Switch from high to low, i.e. put episode 1 at position 0

	#video_xpath = '//*[@id="video-js"]/button/span[1]' # Inside iframe, selenium cant find it. Not sure how to handle that...
	
	#video_xpath = '/html/body/div' # Overarching container click causes video to play
	## Problem is, cant find way to access video controls inside iframe
	# Selenium has ways to step into and out of iFrames. Need to add to Browser
	#Instead, just execute javascript! Most powerful thing selenium offers
	driver.execute_script('document.querySelector("#video-js > div.vjs-poster").click()')
	# No idea how to download it though. I see the link ( I think ), but how to write it to a file?


	for i in links:
		print(i.text)
		#i.click()
		#sleep(3)
		#video = driver.find_element_by_xpath(video_xpath)
		#video.click()	

if __name__=="__main__":
	main()	
