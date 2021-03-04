from Browser import Browser
from time import sleep

def main():
    print("Selenium demo_0 : duckduckgo\n")
    #path = input("Please enter the path to the geckodriver: ")
    path = "/Volumes/Shadowmere/Drivers/geckodriver"
    b = Browser(path, False) # Instantiate as a full browser, i.e. not headless
    # b = Browser(path) # Headless
    # b = Browser(path, False, "127.0.0.1:8080") # Untested, but theortically can route requests through burp
    # b = Browser(path, False, "", True)   # Set 'tor' to True and route through the TOR network
    ## NOTE: Routing through tor cannot be done using the proxy settings

    print("\nGET hxxps://duckduckgo.com/\n")
    b.get("https://duckduckgo.com/") # This is a blocking call
    sleep(1)        # However, ( I think ) it only blocks until DOM loads, not until javascript finishes altering the DOM
    # depending on the page, sleep statements may be required
    print("Find the search bar element on the page")
    search_bar = b.findName("q")  # This can be achieved multiple ways, this was just the shortest
    # search_bar = b.findId("search_form_input_homepage")
    # search_bar = b.findXpath('//*[@id="search_form_input_homepage"]')
    # You get the picture...if its a part of the DOM, it can be found somehow

    print("We can send keys directly to the element..\n")
    # Now that we have the search_bar element, we can directly send keys to it
    b.sendKeys("SendKeys directly to given element", search_bar)
    sleep(7)
    b.clear(search_bar) # Here we just clear out the search bar. The underlying call is simply 'WebElement.clear()'
    ## NOTE: Clearing causes loss of focus, so we need to refocus on the element
    # We can click on the element
    print("We can click on the element and then send keys without specifying an element...\n")
    b.click(search_bar) 
    b.sendKeys("Click. Send Keys") # SendKeys without specifying element will send keys to the currently focused element
    sleep(7)
    b.clear(search_bar) 

    # We can move the cursor to the element....
    # Well, I thought we could. This will have to be ironed out. Not sure why it doesnt work.

    # b.movetoElement(search_bar)
    # b.click() # Click on the current location of the cursor
    # b.sendKeys("Move. Click. Send Keys.")
    # sleep(2)

    #b.clear(search_bar)
    print("Here we just send keys to the element and hit Enter\n")
    b.sendKeys("Selenium is awesome", search_bar)
    b.enter() # Press the Enter Key
    print("\n\nWe play a dangerous game here. No blocking calls or conditional waits.")
    print("So, we take a cat-nap and hope it finishes...\n")
    sleep(7)

    b.quit()

    print("\nThe thread that returns is using sleep statements...")
    print("So the wait time to close can range from 0-10 seconds")
    print("Need a better solution for the polling thread, but havent found one yet.\n")

if __name__=="__main__":
    main()

    

    
    
    