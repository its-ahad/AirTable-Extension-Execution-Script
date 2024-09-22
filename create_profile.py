import pathlib
import os
import shutil
import csv
from fake_headers import Headers
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.common import Keys
from DrissionPage.common import By
import time
import psutil
import json

def kill_chrome():
    # close all chrome instances
    for proc in psutil.process_iter():
        try:
            if 'chrome' in proc.name():
                proc.kill()
            if 'uc_chrome' in proc.name():
                proc.kill()
        except:
            pass


kill_chrome()
PROFILES_FOLDER = pathlib.Path(__file__).parent.joinpath('profiles')
if not os.path.exists(PROFILES_FOLDER): 
    os.makedirs(PROFILES_FOLDER)

# Load credentials from the JSON file with exception handling
try:
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)
    
    url = credentials['url']
    email = credentials['email']
    password = credentials['password']
    profile_folder = email.split('@')[0]
except FileNotFoundError:
    print("Error: The file 'credentials.json' was not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from 'credentials.json'.")
    exit(1)
except KeyError as e:
    print(f"Error: Missing key in credentials file: {e}")
    exit(1)


# Delete profile folder if it exists
user_profile_path = PROFILES_FOLDER / profile_folder
if os.path.exists(user_profile_path):
    shutil.rmtree(user_profile_path)

# Generate headers and user agent
header = Headers(headers=False).generate()
user_agent = header['User-Agent']

# Set up Chromium options
options = ChromiumOptions()
options.headless = False
options.set_argument('--disable-dev-shm-usage')
options.set_argument("--log-level=3")
prefs = {
    "intl.accept_languages": 'en_US,en',
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.geolocation": 2,
    "download_restrictions": 3
}
for key, value in prefs.items():
    options.set_pref(key, value)
options.set_argument("--mute-audio")
options.set_argument('--disable-features=UserAgentClientHint')

# Set the user profile directory
proxy_extension_folder = PROFILES_FOLDER / profile_folder
options.set_argument(f'--user-data-dir={proxy_extension_folder}')

# Initialize Chromium driver
driver = ChromiumPage(addr_or_opts=options)

try:
    # Google login
    driver.get(url)
    time.sleep(3)
    driver.ele('#emailLogin').input(email)
    time.sleep(2)
    driver.run_js('document.querySelector(\'button[type="submit"]\').click();')
    time.sleep(2)
    driver.ele('#passwordLogin').input(password)
    time.sleep(2)
    driver.run_js('document.querySelector(\'button[type="submit"]\').click();')
    input('Press Enter after saving the password to close the browser')

finally:
    driver.quit()
kill_chrome()