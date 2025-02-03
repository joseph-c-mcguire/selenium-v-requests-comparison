import time
import requests
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt

# URL for a JavaScript-heavy website (example: LinkedIn job search)
selenium_url = "https://example.com"

# API URL (example: OpenWeather API)
api_url = "https://catfact.ninja/fact"


def measure_requests():
    """Measures the time taken to fetch data using the requests library."""
    start_time = time.time()
    response = requests.get(api_url)
    end_time = time.time()

    if response.status_code == 200:
        print("API response received successfully.")
    else:
        print("Failed to fetch API data.")

    return end_time - start_time


def install_chrome_if_needed():
    """Check if Chrome is installed; if not, download and install it."""
    # Attempt to run 'chrome --version'. If this fails, assume Chrome is not installed.
    try:
        subprocess.run(["chrome", "--version"], check=True, capture_output=True)
    except:
        print("Chrome not found. Downloading and installing now...")
        installer_path = "chrome_installer.exe"
        url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
        # Download the installer
        with open(installer_path, "wb") as f:
            f.write(requests.get(url).content)
        # Run the installer silently (user may need to accept dialogs)
        subprocess.run([installer_path, "/silent", "/install"])


def measure_selenium():
    """Measures the time taken to fetch data using Selenium."""
    install_chrome_if_needed()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode to speed up execution

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    start_time = time.time()
    driver.get(selenium_url)
    time.sleep(5)  # Wait for JavaScript to load
    job_titles = driver.find_elements(By.CLASS_NAME, "job-card-list__title")

    end_time = time.time()
    driver.quit()

    print(f"Scraped {len(job_titles)} job listings using Selenium.")
    return end_time - start_time


# Collect execution times
requests_times = []
selenium_times = []
for _ in range(30):
    requests_times.append(measure_requests())
    selenium_times.append(measure_selenium())

# Generate and save box-and-whisker plot
plt.boxplot([requests_times, selenium_times], labels=["Requests", "Selenium"])
plt.savefig("comparison_boxplot.png")
