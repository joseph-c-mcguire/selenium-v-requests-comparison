import time
import requests
import subprocess
import logging
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run performance comparison.")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

# Configure logging
if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# URL for a JavaScript-heavy website (example: LinkedIn job search)
API_URL = "https://catfact.ninja/fact"
SELENIUM_URL = "https://example.com"

CHROME_EXECUTABLE_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"


def measure_requests(api_url):
    """
    Measures the time taken to fetch data using the requests library.
    Args:
        api_url (str): The URL of the API endpoint to fetch data from.
    Returns:
        float: The time taken to fetch the data in seconds.
    """
    logging.debug("Starting measure_requests...")
    """Measures the time taken to fetch data using the requests library."""
    start_time = time.time()
    response = requests.get(api_url)
    end_time = time.time()

    logging.debug(f"API response status code: {response.status_code}")
    if response.status_code == 200:
        print("API response received successfully.")
    else:
        print("Failed to fetch API data.")

    logging.debug("Finished measure_requests.")
    return end_time - start_time


def install_chrome_if_needed() -> None:
    """
    Checks if Google Chrome is installed on the system. If Chrome is not found, it downloads and installs the latest version.

    The function attempts to run 'chrome --version' to check for Chrome's presence. If this command fails, it assumes Chrome is not installed and proceeds to:
    1. Download the Chrome installer from the official Google Chrome website.
    2. Save the installer to a file named 'chrome_installer.exe'.
    3. Run the installer silently to install Chrome.

    Logging is used to provide debug information about the process.
    """
    logging.debug("Checking if Chrome is installed...")
    """Check if Chrome is installed; if not, download and install it."""
    # Attempt to run 'chrome --version'. If this fails, assume Chrome is not installed.
    try:
        subprocess.run(
            [CHROME_EXECUTABLE_PATH, "--version"], check=True, capture_output=True
        )
    except:
        logging.debug("Chrome not found. Downloading and installing now...")
        print("Chrome not found. Downloading and installing now...")
        installer_path = "chrome_installer.exe"
        url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
        # Download the installer
        with open(installer_path, "wb") as f:
            f.write(requests.get(url).content)
        # Run the installer silently (user may need to accept dialogs)
        subprocess.run([installer_path, "/silent", "/install"])
    logging.debug("Chrome installation check complete.")


def measure_selenium(selenium_url: str) -> float:
    """
    Measures the time taken to fetch data using Selenium.
    Args:
        selenium_url (str): The URL to be fetched using Selenium.
    Returns:
        float: The time taken to fetch the data in seconds.
    """
    logging.debug("Starting measure_selenium...")
    """Measures the time taken to fetch data using Selenium."""
    install_chrome_if_needed()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode to speed up execution
    options.binary_location = CHROME_EXECUTABLE_PATH

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    logging.debug("Chrome WebDriver initialized.")

    start_time = time.time()
    driver.get(selenium_url)
    time.sleep(5)  # Wait for JavaScript to load
    job_titles = driver.find_elements(By.CLASS_NAME, "job-card-list__title")

    end_time = time.time()
    driver.quit()

    logging.debug(f"Scraped {len(job_titles)} job listings using Selenium.")
    logging.debug("Finished measure_selenium.")
    return end_time - start_time


# Collect execution times
requests_api_times = []
selenium_api_times = []
requests_text_times = []
selenium_text_times = []

for _ in range(5):
    requests_api_times.append(measure_requests(API_URL))
    selenium_api_times.append(measure_selenium(API_URL))
    requests_text_times.append(measure_requests(SELENIUM_URL))
    selenium_text_times.append(measure_selenium(SELENIUM_URL))

plt.boxplot(
    [requests_api_times, selenium_api_times, requests_text_times, selenium_text_times],
    labels=["API - Requests", "API - Selenium", "Text - Requests", "Text - Selenium"],
)
plt.savefig("comparison_boxplot.png")
