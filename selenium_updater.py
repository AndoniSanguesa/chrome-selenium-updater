import os
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
import re
import requests
import wget
import zipfile
import shutil


def update_chrome_drivers(options=Options()):
    # Finds all directories associated with the PATH environment variable
    path_directories = os.getenv("Path").split(";")

    # Determines the directory the chromedriver is located in
    correct_path = None
    for path_directory in path_directories:
        if "chromedriver.exe" in os.listdir(path_directory):
            correct_path = path_directory
            break

    # If the chromedriver is not found, exit the program
    if correct_path is None:
        print("Chromedriver not found, please install and set the PATH environment variable")
        return

    version_needed = -1

    # Runs Selenium to determine which version of the chromedriver is needed
    try:
        driver = webdriver.Chrome(chrome_options=options)
        browser_version = driver.capabilities["browserVersion"].split(".")[0]
        driver_version = driver.capabilities["chrome"]["chromedriverVersion"].split(".")[0]
        driver.close()
        if browser_version == driver_version:
            return
        
        version_needed = browser_version

    except SessionNotCreatedException as e:
        if "only supports" not in e.msg:
            raise e
        version_needed = re.search(r"is (\d+)\.", e.msg).group(1)

    # Finds and downloads the latest chromedriver version
    base_url = "https://chromedriver.storage.googleapis.com"
    driver_version = requests.get(f"{base_url}/LATEST_RELEASE_{version_needed}").text.strip()
    wget.download(f"{base_url}/{driver_version}/chromedriver_win32.zip")

    # Checks for download completion
    if "chromedriver_win32.zip" not in os.listdir("./"):
        print("Download failed")
        return

    # Extracts the chromedriver
    with zipfile.ZipFile("./chromedriver_win32.zip", 'r') as zip_ref:
        zip_ref.extractall("./")

    # Validates extraction
    if "chromedriver.exe" not in os.listdir("./"):
        print("Extraction failed")
        return

    # Deletes old driver and moves new one to the correct location
    shutil.move(f"./chromedriver.exe", f"{correct_path}/chromedriver.exe")
    os.remove("./chromedriver_win32.zip")

    # Validates update allowed Selenium to run
    try:
        webdriver.Chrome(chrome_options=options)
        print("Chrome drivers updated to version {}".format(driver_version))
        return
    except Exception as e:
        print(f"Update failed: {e}")

