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
    
    chrome_service = Service(executable_path="C:/Users/parni/OneDrive/Desktop/ebayScraper/ebay_scraper/chromedriver-win64/chromedriver.exe")
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
    """ Scrolls down the page to load more products dynamically. """
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(delay)



# ============================
# 🟡 Function: Extract Product Data from Search Results
# ============================
def extract_products_from_page(driver):
    """
    Extracts product titles, prices, and URLs from the current search results page.
    """
    product_data = []  # Initialize an empty list to store product data
    try:
        # Locate all product items on the page
        products = driver.find_elements(By.XPATH, '//li[contains(@class, "brwrvr__item-card brwrvr__item-card--gallery")]')
        for product in products:  # Iterate through each product element
            try:
                # Extract product title, price, and URL
                title_element = product.find_element(By.XPATH, './/h3[contains(@class, "textual-display bsig__title__text")]')
                price_element = product.find_element(By.XPATH, './/span[contains(@class, "textual-display bsig__price bsig__price--displayprice")]')
                link_element = product.find_element(By.XPATH, './/a[contains(@class, "bsig__title__wrapper")]')

                
                title = title_element.text.strip() if title_element else "N/A"   # Get title text
                price = price_element.text.strip() if price_element else "N/A"   # Get price text
                url = link_element.get_attribute('href') if link_element else "N/A"   # Get product UR
                
                product_data.append({"Title": title, "Price": price, "URL": url})  # Store extracted data
                print(f"📦 Extracted: {title} | {price}")  # Print extracted product info
            except Exception as e:
                print(f"⚠️ Error extracting product data: {e}")  # Handle extraction errors
    except Exception as e:
        print(f"❌ Error extracting products from page: {e}")  # Handle overall extraction errors
    return product_data  # Return extracted product data


# ============================
# 🟡 Function: Extract All Product Data Across Pages
# ============================
def extract_all_products(driver, max_pages=2):
    """
    Extracts product data across multiple pages.
    """
    all_data = []  # Initialize list to store all product data
    
    for page in range(1, max_pages + 1):   # Loop through the specified number of pages
        print(f"📄 Scraping page {page}...")  # Indicate the current page being scraped

        products = extract_products_from_page(driver)  # Extract products from the current page
        print(f"🔍 Found {len(products)} products on page {page}")  # Display the number of products found
        
        if products:
            all_data.extend(products)  # Add extracted products to the main list
        else:
            print("⚠️ No products found, stopping extraction.")   # Stop extraction if no products found
            break

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.pagination__next")  # Locate the next page button
            driver.execute_script("arguments[0].click();", next_button)  # Click the next page button
            time.sleep(3)  # Ensure the next page loads
        except Exception as e:
            print(f"❌ No more pages or error: {e}")  # Handle pagination errors
            break  # Stop if no more pages are available
    
    print(f"✅ Extracted {len(all_data)} products in total.")
    return all_data  # Return all extracted product data



# ============================
# 🟡 Function: Search on eBay
# ============================
def search_ebay(driver):
    """
    Opens eBay and waits for the user to perform a search manually.
    """
    try:
        driver.get("https://www.ebay.com/")
        input("🔹 Please go to the search bar and perform a search. Press Enter when you're ready...")
        print("✅ Waiting for you to perform the search...")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "gh-ac"))
        )
        input("🔹 After you've searched, press Enter to continue...")
    except Exception as e:
        print(f"❌ Error during search: {e}")



# ============================
# 🟡 Main Function
# ============================
def main():
    """ Main function to scrape eBay data. """
    driver = setup_driver()  # Initialize WebDriver
    driver.get("https://www.ebay.com/")  # Open eBay website
    
    input("🔹 Perform a search on eBay and press Enter when ready...")   # Wait for user to perform a search

    # Extract product data from current page and possibly multiple pages
    all_products = extract_all_products(driver, max_pages=2) # Extract products from eBay
    
    # Save data to DataFrame and CSV
    df = pd.DataFrame(all_products)  # Convert extracted data to DataFrame
    df.to_csv("ebay_products.csv", index=False)  # Save data to CSV file
    
    driver.quit()
    print(all_products)
    print("✅ Scraping completed. Data saved to ebay_products.csv")  # Indicate completion


# ============================
# 🚀 Execute Main Function
# ============================

nest_asyncio.apply()  # Allow nested async loops
asyncio.run(main())   # Run the main function asynchronously


