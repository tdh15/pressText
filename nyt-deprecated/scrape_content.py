# nyt/scrape_content.py
# Scrape content of the articles
# Unsuccessful scraping attempt.

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time



def scrape_article_content(url):
    
    options = Options()
    # Uncomment the next line if you wish to run Chrome headlessly
    # options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    profile_path = r'/Users/thomashughes/Library/Application Support/Google/Chrome/Profile 3'
    options.add_argument(f"user-data-dir={profile_path}")

    # Setup ChromeDriver to automatically manage the driver version
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(8)  # Wait for the dynamic content to load

    content = []
    
    # Fetch and format title
    title = driver.find_element(By.XPATH, '//h1').text
    content.append(f"*{title}* \n\n")  # Title with asterisks
    
    # Fetch and format headers
    headers = driver.find_elements(By.XPATH, '//h2')
    for header in headers:
        content.append(f"*{header.text}* \n\n")
    
    # Fetch and format text blocks
    paragraphs = driver.find_elements(By.XPATH, '//p')
    for paragraph in paragraphs:
        content.append(f"{paragraph.text} \n\n")
    
    # Close the driver
    driver.quit()
    
    return "".join(content)

# Example usage
url = "https://www.nytimes.com/2024/04/01/us/politics/uss-cole-judge-gitmo.html"
article_content = scrape_article_content(url)
print(article_content)