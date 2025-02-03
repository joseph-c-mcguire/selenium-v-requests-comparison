"""
Comparison Tool between Selenium and Requests
------------------------------------------------
This script measures the performance of fetching data using the 'requests'
library and Selenium. It collects execution times for API and a JavaScript 
rendered webpage, then generates a boxplot to compare the results.

Usage:
    python comparison.py [--debug]

Ensure Google Chrome is installed for Selenium to work.
"""

import time
import requests
import logging
import argparse
import os  # Added to check for Chrome binary
import tempfile  # Added for temporary user data dir
import shutil  # Added for cleaning up the temporary directory
import socket  # Added for free port lookup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt

# URL for endpoints and global configuration:
# API_URL: Endpoint for data via Requests.
# SELENIUM_URL: URL of a JavaScript-heavy page for Selenium tests.
API_URL = r"https://catfact.ninja/fact"
SELENIUM_URL = r"https://example.com"
BOXPLOT_FILENAME = "comparison_boxplot.png"
# Define the path to the Chrome binary
CHROME_EXECUTABLE_PATH = r"chrome_installer.exe"
# Define a list of default Chrome binary locations
CHROME_BINARY_LOCATIONS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
# Define a global flag to cache the chrome installation status
IS_CHROME_INSTALLED = True
# Number of times to run the experiments
EXPERIMENT_COUNT = 5


# New function to look up the Chrome binary
def find_chrome_binary() -> str:
    """
    Finds the Chrome binary in default locations or via PATH.

    Returns:
        str: Chrome binary path if found; otherwise an empty string.
    """

    for path in CHROME_BINARY_LOCATIONS:
        if os.path.exists(path):
            return path
    chrome = shutil.which("chrome")
    if chrome:
        return chrome
    return ""


def install_chrome_if_needed() -> None:
    """
    Finds and verifies the presence of the Chrome binary.

    Updates global variables CHROME_EXECUTABLE_PATH and IS_CHROME_INSTALLED.
    Exits if Chrome is not found.
    """
    global IS_CHROME_INSTALLED, CHROME_EXECUTABLE_PATH
    # Reset global state before checking
    IS_CHROME_INSTALLED = False
    CHROME_EXECUTABLE_PATH = r"chrome_installer.exe"
    logging.debug("Searching for Chrome binary...")
    chrome_path = find_chrome_binary()
    if chrome_path:
        CHROME_EXECUTABLE_PATH = chrome_path
        IS_CHROME_INSTALLED = True
        logging.debug(f"Found Chrome at {CHROME_EXECUTABLE_PATH}")
    else:
        IS_CHROME_INSTALLED = False
        logging.error("No Chrome binary found. Please install Chrome manually.")
        exit(1)


def measure_requests(api_url):
    """
    Measures and returns the execution time for fetching data using the requests library.

    Args:
        api_url (str): The API endpoint URL.

    Returns:
        float: Duration in seconds.
    """
    logging.debug("Starting measure_requests...")
    # Start time measurement
    start_time = time.time()
    response = requests.get(api_url)
    end_time = time.time()
    # Log response status code for debugging
    logging.debug(f"API response status code: {response.status_code}")
    if response.status_code == 200:
        print("API response received successfully.")
    else:
        print("Failed to fetch API data.")
    logging.debug("Finished measure_requests.")
    return end_time - start_time


def get_free_port() -> int:
    """
    Returns a free port on localhost.

    Useful for assigning a unique remote debugging port for each Selenium session.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def measure_selenium(selenium_url: str) -> float:
    """
    Measures and returns the time to fetch data using Selenium.

    Uses a temporary user-data-dir and a free remote debugging port to avoid conflicts.

    Args:
        selenium_url (str): The webpage URL to load via Selenium.

    Returns:
        float: Duration in seconds.
    """
    logging.debug("Starting measure_selenium...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU to mitigate encoding issues
    options.add_argument(
        "--disable-features=MediaFoundationVideoEncodeAccelerator"
    )  # Disable MediaFoundation video encode
    # Use a temporary directory for Chrome user profile to avoid conflicts
    with tempfile.TemporaryDirectory() as temp_profile_dir:
        options.add_argument(f"--user-data-dir={temp_profile_dir}")
        free_port = get_free_port()
        options.add_argument(f"--remote-debugging-port={free_port}")
        if IS_CHROME_INSTALLED:
            options.binary_location = CHROME_EXECUTABLE_PATH
        else:
            logging.warning(
                f"Chrome binary not found at {CHROME_EXECUTABLE_PATH}, using default system path."
            )
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.debug("Chrome WebDriver initialized.")

        # Measure page load time
        start_time = time.time()
        driver.get(selenium_url)
        time.sleep(5)  # Allow JavaScript to execute
        job_titles = driver.find_elements(By.CLASS_NAME, "job-card-list__title")
        end_time = time.time()
        driver.quit()
    logging.debug(f"Scraped {len(job_titles)} job listings using Selenium.")
    logging.debug("Finished measure_selenium.")
    return end_time - start_time


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run performance comparison.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Ensure Chrome is installed before running tests
    install_chrome_if_needed()

    # Collect and compare execution times
    requests_api_times = []
    selenium_api_times = []
    requests_text_times = []
    selenium_text_times = []

    for _ in range(EXPERIMENT_COUNT):
        requests_api_times.append(measure_requests(API_URL))
        selenium_api_times.append(measure_selenium(API_URL))
        requests_text_times.append(measure_requests(SELENIUM_URL))
        selenium_text_times.append(measure_selenium(SELENIUM_URL))

    import matplotlib.pyplot as plt
    import numpy as np  # Added for calculations

    groups = [
        requests_api_times,
        selenium_api_times,
        requests_text_times,
        selenium_text_times,
    ]
    tick_labels = [
        "API - Requests",
        "API - Selenium",
        "Text - Requests",
        "Text - Selenium",
    ]
    bp = plt.boxplot(
        groups, labels=tick_labels, patch_artist=True
    )  # Changed from tick_label to labels

    # Set a title and axis labels
    plt.title("Comparison of Performance Metrics")
    plt.xlabel("Method")
    plt.ylabel("Time (seconds)")

    # Annotate each group with mean and standard deviation
    for i, group in enumerate(groups, start=1):
        mean_val = np.mean(group)
        std_val = np.std(group)
        plt.text(
            i,
            mean_val,
            f"mean: {mean_val:.2f}\nstd: {std_val:.2f}",
            horizontalalignment="center",
            verticalalignment="bottom",
            fontsize=8,
            color="blue",
        )

    plt.savefig(BOXPLOT_FILENAME)


if __name__ == "__main__":
    main()
