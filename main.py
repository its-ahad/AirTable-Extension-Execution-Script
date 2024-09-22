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
        for div in divs:
            if 'Data Fetcher' in div.text:
                print("Skipping 'Data Fetcher' div")
                continue
            print(f"Found div with text: {div.text}")
            driver.execute_script("arguments[0].scrollIntoView();", div)
            try:
                iframe = div.find_element(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(iframe)
                run_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Run"]'))
                )
                run_button.click()
                WebDriverWait(driver, 300).until(
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

def start():
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
    wait = WebDriverWait(driver, 60)

    def read_urls(file_path: str) -> list:
        try:
            with open(file_path, 'r') as file:
                urls = file.read().splitlines()
            return urls
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return []
        except Exception as e:
            print(f"An error occurred while reading the file '{file_path}': {e}")
            return []

    urls = read_urls('urls.txt')
    for url in urls:
        try:
            init(autoreset=True)
            print(f"{Fore.CYAN}Processing URL: {url}")
            result = process_url(driver, wait, url)
            if result == "success":
                print(f"{Fore.GREEN}Processed URL: {url} - {result}")
            else:
                print(f"{Fore.RED}Processed URL: {url} - {result}")
        except Exception as e:
                print(f"{Fore.RED}An error occurred while processing URL: {url} - {e}")

    driver.quit()



if __name__ == '__main__':
    kill_chrome()
    start()
