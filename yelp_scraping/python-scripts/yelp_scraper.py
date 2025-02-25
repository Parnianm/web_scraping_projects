
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
# Importing urlparse and parse_qs from urllib.parse to parse URLs and extract query parameters
from urllib.parse import urlparse, parse_qs


# ============================
# 🟡 Helper Function: Setup WebDriver
# ============================
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
    
    chrome_service = Service(executable_path="C:/Users/parni/OneDrive/Desktop/web_scraping_projects/yelp_scraping/drivers/chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # Initialize WebDriver with options
    return driver   # Return the configured WebDriver instance



# ============================
# 🟡 Function: Save & Load Cookies
# ============================
def save_cookies(driver, filename="cookies.json"):
    """ Saves cookies to a JSON file. """
    with open(filename, "w") as file:
        json.dump(driver.get_cookies(), file)
    print("✅ Cookies saved.")

def load_cookies(driver, filename="cookies.json"):
    """ Loads cookies from a JSON file. """
    try:
        with open(filename, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Cookies loaded.")
    except FileNotFoundError:
        print("⚠️ No cookies found. Proceeding without loading cookies.")


# ============================
# 🟡 Function: Scroll Down Page
# ============================
def scroll_down(driver, scroll_times=3, delay=1):
    """ Scrolls down dynamically based on page height. """
    for _ in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)



# ============================
# 🟡 Function: Extract Yelp Business Data from Search Results
# ============================
def extract_businesses_from_page(driver):
    """
    Extracts business names, ratings, and URLs from the current Yelp search results page.
    """
    business_data = []  # Initialize an empty list to store business data
    try:
        # Locate all business items on the page
        businesses = driver.find_elements(By.XPATH, '//div[contains(@class, "container__09f24__FeTO6 y-css-1txhg36")]')
        for business in businesses:  # Iterate through each business element
            try:
                # Extract business name, rating, and URL
                name_element = business.find_element(By.XPATH, './/h3')
                rating_element = business.find_element(By.XPATH, './/div[@class="y-css-dnttlc" and @aria-label]')
                link_element = business.find_element(By.XPATH, './/a[contains(@class, "y-css-1x1e1r2")]')
                
                name = name_element.text.strip() if name_element else "N/A"   # Get business name text
                rating = rating_element.get_attribute("aria-label") if rating_element else "N/A"   # Get rating text
                url = link_element.get_attribute('href') if link_element else "N/A"   # Get business URL
                
                business_data.append({"Name": name, "Rating": rating, "URL": url})  # Store extracted data
                print(f"🏢 Extracted: {name} | {rating}")  # Print extracted business info
            except Exception as e:
                print(f"⚠️ Error extracting business data: {e}")  # Handle extraction errors
    except Exception as e:
        print(f"❌ Error extracting businesses from page: {e}")  # Handle overall extraction errors
    return business_data  # Return extracted business data


# ============================
# 🟡 Function: Extract All Businesses Dynamically from Multiple Pages
# ============================
def extract_all_businesses(driver, search_term, location, max_pages=3):
    """
    Extracts business data across multiple pages with dynamic pagination.
    """
    all_data = []
    
    for page in range(1, max_pages + 1):
        start_value = (page - 1) * 10 + 1
        url = f"https://www.yelp.co.uk/search?find_desc={search_term}&find_loc={location}&start={start_value}"
        
        print(f"📄 Scraping page {page} with start={start_value}...")  
        driver.get(url)
        
        businesses = extract_businesses_from_page(driver)
        print(f"🔍 Found {len(businesses)} businesses on page {page}")
        
        if not businesses:
            print("⚠️ No businesses found, stopping extraction.")
            break
        
        all_data.extend(businesses)
        scroll_down(driver, scroll_times=3, delay=2)

    print(f"✅ Extracted {len(all_data)} businesses in total.")
    return all_data



# ============================
# 🟡 Function: Get Search Term from URL
# ============================

def get_search_term_from_url(url):
    """
    Extracts the search term from the Yelp search URL.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    search_term = query_params.get('find_desc', [''])[0]  # Extract 'find_desc' parameter
    return search_term



# ============================
# 🟡 Function: Extract Location from URL
# ============================
def get_location_from_url(url):
    """
    Extracts the location from the Yelp search URL.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    location = query_params.get('find_loc', [''])[0]  # Extract 'find_loc' parameter
    return location



# ============================
# 🟡 Main Function
# ============================
def main():
    """ Main function to scrape Yelp data. """
    driver = setup_driver()
    driver.get("https://www.yelp.com/")
    
    input("🔹 Perform a search on Yelp and press Enter when ready...")
    
    current_url = driver.current_url
    search_term = get_search_term_from_url(current_url)
    location = get_location_from_url(current_url)  # Automatically extract location from the URL
    
    print(f"🔍 Extracted search term: {search_term} | Location: {location}")
    
    if not search_term or not location:
        print("⚠️ Missing search term or location. Exiting.")
        driver.quit()
        return
    
    all_businesses = extract_all_businesses(driver, search_term, location, max_pages=3)
    
    # Save data to DataFrame and CSV
    df = pd.DataFrame(all_businesses)
    df.to_csv("yelp_businesses.csv", index=False)
    
    driver.quit()
    print(all_businesses)
    print("✅ Scraping completed. Data saved to yelp_businesses.csv")




# ============================
# 🚀 Execute Main Function
# ============================

nest_asyncio.apply()  # Allow nested async loops
# Run the main function 

if __name__ == "__main__":
    main()  



