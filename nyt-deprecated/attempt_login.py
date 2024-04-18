# This is an attempt to log into Chrome with a specific profile for scraping.
# It didn't work, but it's a good starting point for further exploration.

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess

def login_with_profile(url):
    
    print("Setting up Chrome options...")
    options = Options()

    options.add_argument('log-level=3')
    
    # Specify the path to your Chrome profile
    profile_path = r'/Users/thomashughes/Library/Application Support/Google/Chrome/Profile 3'
    options.add_argument(f"user-data-dir={profile_path}")
    print(f"Profile path set to: {profile_path}")
    
    print("Setting up ChromeDriver...")
    # Setup ChromeDriver to automatically manage the driver version
    try:
        service = Service(executable_path=ChromeDriverManager().install())
        print("ChromeDriver setup successfully.")
    except Exception as e:
        print(f"Error setting up ChromeDriver: {e}")
        return
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver initialized with profile.")
    except Exception as e:
        print(f"Error initializing ChromeDriver with profile: {e}")
        return

    # Navigate to the specified URL
    print(f"Navigating to {url}...")
    driver.get(url)
    
    # Keep the browser open for a while to observe, adjust time as needed
    time.sleep(30)
    
    # Close the driver
    print("Closing the browser...")
    driver.quit()
    print("Browser closed successfully.")

# Command to kill all instances of Chrome
# try:
#     subprocess.run(["pkill", "Chrome"], check=True)
#     print("Closed all running Chrome instances.")
# except subprocess.CalledProcessError as e:
#     print(f"Error closing Chrome instances: {e}")


# Example usage: adjust the URL to a specific page you want to open with the profile
url = "https://www.google.com"
login_with_profile(url)
