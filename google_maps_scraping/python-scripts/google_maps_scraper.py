
import time   # Import time module for delays
import json   # Import JSON module for handling cookies
import random  # Import random module to select user agents
import asyncio  # Import asyncio for async execution
import nest_asyncio  # Import nest_asyncio to allow nested async loops
from selenium import webdriver  # Import Selenium WebDriver
from selenium.webdriver.common.by import By  # Import By class for locating elements
from selenium.webdriver.chrome.service import Service  # Import Service for ChromeDriver
from selenium.webdriver.chrome.options import Options  # Import Options to configure WebDriver
from selenium.webdriver.support.ui import WebDriverWait   # Import WebDriverWait for explicit waits
from selenium.webdriver.support import expected_conditions as EC  # Import expected_conditions for conditions
import pandas as pd  # Import pandas for handling and saving extracted data


def setup_driver():
    """
    Initializes and configures Selenium WebDriver with performance optimizations.
    """
    user_agents = [  # List of user agents to avoid detection
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0)",
    ]
    
    chrome_options = Options()  # Create Chrome options object
     # Running in headless mode for efficiency (Uncomment if needed)
    # chrome_options.add_argument('--headless')  # Run browser in headless mode
    chrome_options.add_argument('--disable-blink-features=AutomationControlled') # Bypass automation detection
    chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')  # Randomize user-agent
    chrome_options.add_argument('--start-maximized') # Open browser in maximized mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration for stability
    chrome_options.add_argument('--log-level=3')  # Suppress unnecessary logs
    chrome_options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Disable automation flags
    
    chrome_service = Service(executable_path="C:/Users/parni/OneDrive/Desktop/GoogleMap/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # Initialize WebDriver with options
    return driver   # Return the configured WebDriver instance



def open_google_maps(driver):
    """Open Google Maps website and wait for user interaction."""
    driver.get("https://www.google.com/maps")
    input("Solve CAPTCHA or accept cookies, then press Enter to continue...")
    time.sleep(3)

    


def search_location(driver, query):
    """Allow the user to manually search for a location on Google Maps."""
    try:
        # Find the search box and enter the query
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(query)

        # Ask the user to manually press Enter after locating the desired location
        print(f"Please go to the location for '{query}' and press Enter when ready.")
        
        # Wait for the user to press Enter
        input("Press Enter to continue...")

        # Allow time for the page to load after the user presses Enter
        time.sleep(5)
    
    except Exception as e:
        print("Error searching location:", e)



def extract_places(driver, num_places):
    """Extract names and addresses of places from search results using XPath."""
    results = []
    
    # Scroll down to load more places until the required number is reached
    while len(results) < num_places:
        places = driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')  # Find all the places using XPath
        
        for place in places:
            try:
                # Extract name (from aria-label attribute or text inside the <a> tag)
                name = place.get_attribute("aria-label")  # The name is stored in the aria-label attribute
                
                # Extract the link (href) of the place
                link = place.get_attribute("href")  # The link to the place

                results.append((name, link))  # Add both name and link to results

                if len(results) >= num_places:
                    break  # Stop if we have enough places
                
            except Exception as e:
                print("Error extracting data:", e)
        
        # Scroll to the bottom of the page to load more places
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait a bit longer for more places to load
        
        # Check if new places have been loaded
        if len(results) < num_places:
            print(f"Loaded {len(results)} places, continuing to scroll...")

    return results



def main():
    """Main function to execute the scraper."""
    driver = setup_driver()
    open_google_maps(driver)
    input("Press Enter after Google Maps is fully loaded...")
    search_location(driver, "Restaurants in New York")
    
    # Ask the user how many places they want to extract
    num_places = int(input("How many places would you like to extract? "))
    
    # Extract the places
    results = extract_places(driver, num_places)
    
    # Display the extracted places
    for name, address in results:
        print(f"Name: {name}, Address: {address}")
    
    driver.quit()


if __name__ == "__main__":
    main()


