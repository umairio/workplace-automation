import json
import os
import time
import traceback
from pprint import pprint

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from discobot import send_discord_message
from logger import logger

load_dotenv()

path = (
    ChromeDriverManager().install()
    .replace('chromedriver-linux64/THIRD_PARTY_NOTICES.chromedriver', 'chromedriver-linux64/chromedriver')
    .replace('chromedriver-win32/THIRD_PARTY_NOTICES.chromedriver', r'chromedriver-win32\chromedriver.exe')
)
if "linux" in path:
    os.chmod(path, 0o755)

# path = os.environ.get("DRIVER_PATH")
def initiate_driver():
    """
    :return: webdriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options, service=Service(path))
    driver.execute_script("document.body.style.zoom='70%'")
    return driver


def checkin_job(username, passwrd, user_id):
    """
    :param username: str
    :param passwrd: str
    :param user_id: str
    :return: None 

    """
    def checkin(driver):
        """
        :param driver: webdriver
        :return: str, webdriver
        """
        driver.execute_script("document.body.style.zoom='70%'")
        checkin = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="dashboard-here"]/div/div[3]/mark-attendance/section/div[2]/div/div/ng-transclude/div/div[3]/button[1]',
            ))
        )
        action = ActionChains(driver)
        time.sleep(1)
        action.move_to_element(checkin).perform()
        time.sleep(1)
        checkin.click()
        time.sleep(2)
        result = "Success"
        logger.info(f"{username} checked-in successfully")
        return result, driver

    logger.info(f"Check-in job started for: {username}")
    result = str

    try:
        driver = initiate_driver()

        logger.info("Webdriver initiated")

        url = "https://linkedmatrix.resourceinn.com/#/core/login"
        driver.get(url)
        logger.info(f"Navigated to {url}")

        username_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        logger.info("Username field located")
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
        logger.info("Password field located")

        logger.info(f"Attempting to log in for: {username}")
        password_field.send_keys(passwrd)

        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()
        logger.info("Login button located and clicked and redirecting")
        rml = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="wrap"]/div/div/div[2]/div/section/div[2]/div/button',))
        )
        rml.click()
        # driver.get("https://linkedmatrix.resourceinn.com/#/app/dashboard")
        # logger.info("Redirecting to dashboard")
        try:
            result, driver = checkin(driver)
        except StaleElementReferenceException:
            logger.info("stale element reference, Refreshing the page")
            driver.get("https://linkedmatrix.resourceinn.com/#/app/dashboard")
            result, driver = checkin(driver)
        except TimeoutException:
            checkout = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="dashboard-here"]/div/div[3]/mark-attendance/section/div[2]/div/div/ng-transclude/div/div[3]/button[2]',
            )))
            if checkout:
                action = ActionChains(driver)
                time.sleep(1)
                action.move_to_element(checkout).perform()
                time.sleep(1)
                result = "Already-checked-in"
                logger.info(f"Already checked-in for {username}")
        driver.execute_script("document.body.style.zoom='70%'")
        ss = driver.save_screenshot("checkin.png")

        #send discord messages
        if result == "Success":
            if ss:
                content = f"{user_id} Checked-in successfully"
                logger.info(f"Screenshot captured for {username}")
                send_discord_message(content, image='checkin.png')
            else:
                send_discord_message(content)

        logger.info("Job completed successfully")
    except Exception:
        result = "Failed"
        logger.error(f"An error occurred for {username}: {traceback.format_exc()}")
    finally:
        driver.quit()
        logger.info("Webdriver closed")
        return result


def main(result):
    usernames = os.environ.get("USERNAMES", "").split(',')
    passwords = os.environ.get("PASSWORDS", "").split(',')
    leave_users = os.environ.get("LEAVE_USERS", "").split(',')
    user_ids = os.environ.get("DISCORD_USER_IDS", "").split(',')
    # emails = os.environ.get("EMAILS", "").split(',')
    if len(leave_users[0]):
        print(leave_users)
    if len(usernames) != len(passwords):
        logger.error("The number of emails does not match the number of passwords")
        return
    data = list(zip(usernames, passwords, user_ids))
    if not result:
        for username, password, user_id in data:
            result[username] = checkin_job(username, password, user_id) if username not in leave_users else "Leave"
        pprint(result)

    # if failed result
    while "Failed" in result.values():
        logger.info("Retrying failed jobs")
        for username, password, user_id in data:
            if result[username] == "Failed":
                result[username] = checkin_job(username, password, user_id)
        pprint(result)

    logger.info(f"All jobs completed successfully {result}")
    send_discord_message("```python\n"+json.dumps(result, indent=4)+"```")
