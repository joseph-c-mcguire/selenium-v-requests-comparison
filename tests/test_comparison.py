import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import os  # Added missing import
import shutil  # Added missing import
from unittest.mock import patch, MagicMock
import pytest
import logging
import time
import requests
from selenium.webdriver.common.by import By

from selenium_v_requests_comparison.comparison import (
    install_chrome_if_needed,
    IS_CHROME_INSTALLED,
    CHROME_EXECUTABLE_PATH,
    measure_requests,
    measure_selenium,
)

CHROME_BINARY_LOCATIONS = [
    "/usr/bin/google-chrome",
    "/usr/local/bin/google-chrome",
    "/opt/google/chrome/google-chrome",
]


def find_chrome_binary():
    for location in CHROME_BINARY_LOCATIONS:
        if os.path.exists(location):
            return location
    return shutil.which("google-chrome")


def test_find_chrome_binary_in_default_locations():
    with patch("os.path.exists") as mock_exists:
        # Mock os.path.exists returns True for the first location
        mock_exists.side_effect = lambda path: path == CHROME_BINARY_LOCATIONS[0]
        result = find_chrome_binary()
        assert result == CHROME_BINARY_LOCATIONS[0]


def test_find_chrome_binary_in_path():
    with patch("os.path.exists") as mock_exists, patch("shutil.which") as mock_which:
        # All paths return False; shutil.which returns a valid path
        mock_exists.return_value = False
        mock_which.return_value = "/usr/bin/google-chrome"
        result = find_chrome_binary()
        assert result == "/usr/bin/google-chrome"


def test_install_chrome_if_needed_found():
    with patch(
        "selenium_v_requests_comparison.comparison.find_chrome_binary"
    ) as mock_find:
        mock_find.return_value = "/usr/bin/google-chrome"
        with patch("selenium_v_requests_comparison.comparison.logging") as mock_logging:
            install_chrome_if_needed()


def test_install_chrome_if_needed_not_found():
    with patch(
        "selenium_v_requests_comparison.comparison.find_chrome_binary"
    ) as mock_find:
        mock_find.return_value = ""
        with (
            patch("selenium_v_requests_comparison.comparison.logging") as mock_logging,
            patch("builtins.exit") as mock_exit,
        ):
            install_chrome_if_needed()
            mock_logging.error.assert_called_with(
                "No Chrome binary found. Please install Chrome manually."
            )
            mock_exit.assert_called_once_with(1)


@patch("selenium_v_requests_comparison.comparison.webdriver.Chrome")
@patch("selenium_v_requests_comparison.comparison.ChromeDriverManager")
@patch("selenium_v_requests_comparison.comparison.get_free_port")
@patch("selenium_v_requests_comparison.comparison.tempfile.TemporaryDirectory")
def test_measure_selenium(
    mock_temp_dir, mock_get_free_port, mock_chrome_driver_manager, mock_webdriver_chrome
):
    SELENIUM_URL = "https://example.com"
    mock_temp_dir.return_value.__enter__.return_value = "/tmp/fake_profile_dir"
    mock_get_free_port.return_value = 9222
    mock_service = MagicMock()
    mock_chrome_driver_manager.return_value.install.return_value = mock_service
    mock_driver = MagicMock()
    mock_webdriver_chrome.return_value = mock_driver
    mock_driver.find_elements.return_value = [MagicMock(), MagicMock()]

    duration = measure_selenium(SELENIUM_URL)
    # Assert the duration is roughly equal to the 5-second sleep (with tolerance)
    assert 4.5 <= duration <= 7.0
    mock_driver.get.assert_called_once_with(SELENIUM_URL)
    mock_driver.quit.assert_called_once()
    mock_driver.find_elements.assert_called_once_with(
        By.CLASS_NAME, "job-card-list__title"
    )


@patch("selenium_v_requests_comparison.comparison.requests.get")
def test_measure_requests_success(mock_get):
    API_URL = "https://catfact.ninja/fact"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    start_time = time.time()
    duration = measure_requests(API_URL)
    end_time = time.time()

    assert 0 <= duration <= (end_time - start_time)
    mock_get.assert_called_once_with(API_URL)


@patch("selenium_v_requests_comparison.comparison.requests.get")
def test_measure_requests_failure(mock_get):
    API_URL = "https://catfact.ninja/fact"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    start_time = time.time()
    duration = measure_requests(API_URL)
    end_time = time.time()

    assert 0 <= duration <= (end_time - start_time)
    mock_get.assert_called_once_with(API_URL)
