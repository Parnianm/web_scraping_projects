import random
import asyncio
import nest_asyncio
import concurrent.futures
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================
# 🟡 Helper Function: Setup WebDriver
# ============================
def setup_driver():
    """
    This function initializes and configures the Selenium WebDriver with custom settings to enhance performance 
    and avoid bot detection mechanisms.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0)",
    ]
    chrome_options = Options()

    # 🟢 Performance and Anti-bot settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Hides Selenium automation flag
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')  # Sets a custom User-Agent
    chrome_options.add_argument('--start-maximized')  # Maximizes browser window
    chrome_options.add_argument('--disable-gpu')  # Disables GPU rendering for performance
    chrome_options.add_argument('--log-level=3')  # Suppresses unnecessary logs
    chrome_options.add_argument('--ignore-certificate-errors')  # Ignores SSL certificate errors
    # chrome_options.add_argument('--proxy-auto-detect')  # Uses system proxy settings
    chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')  # Randomizes user-agent to reduce detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Further hides automation usage

    # 🟡 Sets experimental capabilities to speed up page loading
    caps = webdriver.DesiredCapabilities.CHROME.copy()
    caps['pageLoadStrategy'] = 'eager'  # Loads pages faster by skipping unnecessary resources

    # 🛠 Sets the ChromeDriver executable path
    chrome_service = Service(executable_path="C:/Users/parni/OneDrive/Desktop/automate/chromedriver-win64/chromedriver-win64/chromedriver.exe")

    # 🏎️ Launches the WebDriver with defined options
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver


# ============================
# 🟡 Function: Scroll Down Page
# ============================
def scroll_down(driver, scroll_times=3, delay=2):
    """
    Scrolls down the webpage to load more products dynamically.
    Args:
        driver: Selenium WebDriver instance
        scroll_times (int): Number of times to scroll
        delay (int): Delay between scrolls (seconds)
    """
    for i in range(scroll_times):
        driver.execute_script("window.scrollBy(0, 500);")  # Scrolls down by 500 pixels
        time.sleep(delay)  # Waits for content to load



# ============================ 
# 🟡 Function: Search on Amazon 
# ============================ 
def search_amazon(driver): 
    """
    Opens Amazon and waits for the user to perform a search manually.
    """
    try:
        driver.get("https://www.amazon.com/")  # Loads Amazon homepage
        input("🔹 Please go to the search bar and perform a search. Press Enter when you're ready...")  # Asks user to search manually
        print("✅ Waiting for you to perform the search...")

        # Waits until the search box is visible (no automatic search here, just waiting for user interaction)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        
        print("🔍 Please manually search for the product you're looking for.")
        input("🔹 After you've searched, press Enter to continue...")  # Waits for the user to press Enter after performing search
        print("✅ Proceeding after search...")

    except Exception as e:
        print(f"❌ Error during search: {e}")



# ============================
# 🟡 Function: Extract Product URLs
# ============================
async def extract_product_urls(driver):
    """
    Extracts product URLs from the search results page.
    """
    try:
        scroll_down(driver)  # Scrolls down to load more products

        # Waits until product links are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot a.a-link-normal.s-no-outline'))
        )

        product_links = driver.find_elements(By.CSS_SELECTOR, 'div.s-main-slot a.a-link-normal.s-no-outline')
        product_urls = [
            link.get_attribute('href') for link in product_links
            if link.get_attribute('href') and '/dp/' in link.get_attribute('href')
        ]

        print(f"✅ Found {len(product_urls)} product URLs.")
        return product_urls
    except Exception as e:
        print(f"❌ Error extracting product URLs: {e}")
        return []



# ============================
# 🟡 Function: Extract Product Data and Save to CSV 
# ============================ 
def extract_product_data(driver, url, data_list): 
    """
    Extracts product details like title, price, and reviews from an Amazon product page.
    """
    try:
        driver.get(url)  # Wait for page load asynchronously
        time.sleep(2)  # You may want to use async sleep or waits for better efficiency
        
        # Wait until a specific element is present, using WebDriverWait (asynchronous handling if needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'productTitle'))  # You can replace with any other element that's always on the page
        )


        # Please provide the required selectors for each field
        title_selector = "productTitle"  # Title element
        price_selector = "//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay']//span[@class='a-price-whole']"  # Price element
        description_selector = "feature-bullets"  # Description element
        reviews_selector = "averageCustomerReviews"  # Reviews element
        
        # Helper function to convert ID to XPath
        def id_to_xpath(id_value):
            return f"//*[@id='{id_value}']"  # Converts ID to XPath format

        # Convert IDs to XPath if necessary
        if " " not in title_selector and not title_selector.startswith("/"):  # Assuming ID if no space and no XPath
            title_selector = id_to_xpath(title_selector)
        if " " not in price_selector and not price_selector.startswith("/"):  # Assuming ID if no space and no XPath
            price_selector = id_to_xpath(price_selector)
        if " " not in description_selector and not description_selector.startswith("/"):
            description_selector = id_to_xpath(description_selector)
        if " " not in reviews_selector and not reviews_selector.startswith("/"):
            reviews_selector = id_to_xpath(reviews_selector)

        # Extracts product title
        title_elements = driver.find_elements(By.XPATH, title_selector)
        title = title_elements[0].text.strip() if title_elements else "N/A"
        
        # Extracts product price
        price = "No featured offers available"  # Default value if price not found
        price_elements = driver.find_elements(By.XPATH, price_selector)
        if price_elements:
            price = price_elements[0].text.strip()


        # Extracts product description (if available)
        description = "N/A"
        description_elements = driver.find_elements(By.XPATH, description_selector)
        if description_elements:
            description = description_elements[0].text.strip()
        
        # Extracts reviews (if available)
        reviews = "N/A"
        reviews_elements = driver.find_elements(By.XPATH, reviews_selector)
        if reviews_elements:
            reviews = reviews_elements[0].text.strip()

        # Appends product details to list
        data_list.append({"Title": title, "Price": price, "Reviews": reviews, "URL": url})
        print(f"📦 Extracted: {title} | Price: {price} | Reviews: {reviews}")
    except Exception as e:
        print(f"❌ Error extracting data from {url}: {e}")



# ============================
# 🟢 MAIN FUNCTION
# ============================
async def main():
    """
    Orchestrates the web scraping process and saves data to a CSV file.
    """
    driver = setup_driver()
    search_amazon(driver)
    product_urls = await extract_product_urls(driver)
    data_list = []
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, extract_product_data, driver, url, data_list)
            for url in product_urls
        ]
        await asyncio.gather(*tasks)
    
    df = pd.DataFrame(data_list)
    df.to_csv("amazon_products.csv", index=False)
    print("✅ Data saved to amazon_products.csv")
    driver.quit()
    print("✅ Scraping completed.")



# ============================
# 🚀 Execute Main Function
# ============================

nest_asyncio.apply()
asyncio.run(main())


