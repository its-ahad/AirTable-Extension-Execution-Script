import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pathlib
import json
import psutil
import time
from colorama import Fore, Style, init
import schedule


PROFILES_FOLDER = pathlib.Path(__file__).parent.joinpath('profiles')

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

def process_url(driver:uc.Chrome,wait,url:str):
    try:
        driver.maximize_window()
        driver.get(url)
        time.sleep(2)
        try:
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.react-grid-item.react-draggable.cssTransforms.react-resizable'))
        )
        except:
            # Click on the div with data-tutorial-selector-id="extensions"
            extensions_div = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-tutorial-selector-id="extensions"]'))
            )
            extensions_div.click()
            
        time.sleep(10)

       # Wait and get all the divs with the specified class from the container
        divs = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.react-grid-item.react-draggable.cssTransforms.react-resizable'))
        )

        # Defining the order of actions you want to take (based on the list you shared earlier)
        actions_order = [
            "View gained last 1 Day",
            "Follower gained last 1 Day",
            "View gained last 3 Days",
            "Follower gained last 3 Days",
            "View gained last 7 Days",
            "Follower gained last 7 Days",
            "Average Views last 15 Postings",
            "Average Views last 30 Postings",
            "Average Views last 45 Postings"
        ]
        for action in actions_order:
            for div in divs:
                div_text = div.text.strip()
                if 'Data Fetcher' in div_text:
                    continue
                
                if action == div_text:
                    print(f"Processing div with action: {action}")
                    driver.execute_script("arguments[0].scrollIntoView();", div)
                    time.sleep(5)
                    try:
                        iframe = div.find_element(By.TAG_NAME, 'iframe')
                        driver.switch_to.frame(iframe)
                        run_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, '//span[text()="Run"]'))
                        )
                        run_button.click()
                        WebDriverWait(driver, 80000).until(
                            EC.element_to_be_clickable((By.XPATH, '//span[text()="Run"]'))
                        )
                        print("Run button clicked and reappeared")
                    except Exception as e:
                        print(f"An error occurred while interacting with the iframe: {e}")
                    finally:
                        driver.switch_to.default_content()

        return "success"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "fail"

def process_pages(pages):
    # Load credentials from the JSON file with exception handling
    try:
        with open('credentials.json', 'r') as file:
            credentials = json.load(file)
        profile_folder = credentials['email'].split('@')[0]
    except FileNotFoundError:
        print("Error: The file 'credentials.json' was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from 'credentials.json'.")
        exit(1)
    except KeyError as e:
        print(f"Error: Missing key in credentials file: {e}")
        exit(1)
    user_profile_path = PROFILES_FOLDER / profile_folder
    if not user_profile_path.exists():
        print(f"Error: Profile folder '{user_profile_path}' does not exist.")
        exit(1)
    # Initialize undetected ChromeDriver
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={user_profile_path}")
    driver = uc.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 360)
    for page in pages:
        try:
            init(autoreset=True)
            print(f"{Fore.CYAN}Processing URL: {page}")
            result = process_url(driver, wait, page)
            if result == "success":
                print(f"{Fore.GREEN}Processed URL: {page} - {result}")
            else:
                print(f"{Fore.RED}Processed URL: {page} - {result}")
        except Exception as e:
                print(f"{Fore.RED}An error occurred while processing URL: {page} - {e}")
    driver.quit()

# Schedule tasks
schedule.every().day.at("01:00").do(process_pages, ["https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide", "https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide", "https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide"])
schedule.every().day.at("04:00").do(process_pages, ["https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide", "https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide", "https://airtable.com/appuJhJIynMNeaDAo/tblyrm0NCmCx6iJAE/viwQLT8J8URyD4vHx?blocks=hide"])

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)