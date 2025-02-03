import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import os  # Added missing import
import shutil  # Added missing import
from unittest.mock import patch, MagicMock  # Combined imports
import pytest
import logging
from selenium_v_requests_comparison.comparison import (
    install_chrome_if_needed,
    IS_CHROME_INSTALLED,
    CHROME_EXECUTABLE_PATH,
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
        # Mock os.path.exists to return True for the first path
        mock_exists.side_effect = lambda path: path == CHROME_BINARY_LOCATIONS[0]
        result = find_chrome_binary()
        assert result == CHROME_BINARY_LOCATIONS[0]


def test_find_chrome_binary_in_path():
    with patch("os.path.exists") as mock_exists, patch("shutil.which") as mock_which:
        # Mock os.path.exists to return False for all paths
        mock_exists.return_value = False
        # Mock shutil.which to return a valid path
        mock_which.return_value = "/usr/bin/google-chrome"
        result = find_chrome_binary()
        assert result == "/usr/bin/google-chrome"


def test_install_chrome_if_needed_found():
    with patch(
        "selenium_v_requests_comparison.comparison.find_chrome_binary"
    ) as mock_find_chrome_binary:
        mock_find_chrome_binary.return_value = "/usr/bin/google-chrome"
        with patch("selenium_v_requests_comparison.comparison.logging") as mock_logging:
            install_chrome_if_needed()


def test_install_chrome_if_needed_not_found():
    with patch(
        "selenium_v_requests_comparison.comparison.find_chrome_binary"
    ) as mock_find_chrome_binary:
        mock_find_chrome_binary.return_value = ""
        with patch(
            "selenium_v_requests_comparison.comparison.logging"
        ) as mock_logging, patch("builtins.exit") as mock_exit:
            install_chrome_if_needed()
            mock_logging.error.assert_called_with(
                "No Chrome binary found. Please install Chrome manually."
            )
            mock_exit.assert_called_once_with(1)
