import json
import datetime
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions
from loguru import logger
import time


def load_json_file(file_name):
    try:
        with open(file_name, 'r') as config_file:
            json_data = json.load(config_file)
            return json_data, 0  # Success
    except FileNotFoundError:
        logger.error(f"{file_name} file not found.")
        return None, -1  # JSON file load error
    except KeyError as e:
        logger.error(f"Key {e} is missing in the {file_name} file.")
        return None, -2  # Missing keys in JSON
    except json.JSONDecodeError:
        logger.error(f"Error parsing {file_name}. Ensure the JSON is formatted correctly.")
        return None, -3  # JSON file load error
    except Exception:
        logger.exception(f"An unexpected error occurred while loading {file_name}.")
        return None, -4  # Unknown exception


def upload_to_imgbb(headless_mode, imgbb_username, imgbb_password, imgbb_album_id, working_path, file_list, link_export_types, log_filename):
    """Logs in to ImgBB, navigates to homepage, uploads an image, and saves the direct link to a timestamped text file in the working path."""

    try:
        # Configure ChromeOptions for headless mode
        chrome_options = Options()
        if headless_mode:
            chrome_options.add_argument("--headless=new")  # Use the new headless mode
        else:
            chrome_options = None

        # Initialize the WebDriver with the headless options
        driver = webdriver.Chrome(options=chrome_options)  # Or webdriver.Firefox(), etc.

        # Navigate to the ImgBB login page
        driver.get("https://imgbb.com/login")

        # Wait for the email and password fields to be present and fill them dynamically
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "login-subject"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        email_field.send_keys(imgbb_username)
        password_field.send_keys(imgbb_password)

        # Submit the login form using a more specific XPath for the button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@data-action='validate']//button[@type='submit' and contains(text(), 'Sign in')]"))
        )
        login_button.click()

        # Wait for the login to complete (you might need to adjust the wait condition)
        WebDriverWait(driver, 10).until(EC.url_to_be(f"https://{imgbb_username}.imgbb.com/"))

        # Navigate to the homepage
        driver.get("https://imgbb.com/")

        # Wait for the "Start uploading" button to be clickable
        upload_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='home-cover-content']//a[@data-trigger='anywhere-upload-input' and contains(text(), 'Start uploading')]"))
        )
        # upload_button.click()

        # Wait for the file input field to be present and send the image path
        for file in file_list:
            # logger.debug(file)
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(str(file))  # Send the string representation of the Path object
            time.sleep(0.5)  # Keeping the sleep might be helpful for the page to process

        # Wait for the album select dropdown to be visible
        album_select = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "upload-album-id"))
        )

        # Use the Select class to interact with the dropdown
        album_dropdown = Select(album_select)
        album_dropdown.select_by_value(imgbb_album_id)

        # Wait for the "Upload" button to be clickable and click it
        upload_submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='anywhere-upload-submit']//button[@data-action='upload' and contains(text(), 'Upload')]"))
        )
        upload_submit_button.click()

        # Wait for the upload to complete and the embed codes section to be visible
        embed_codes_div = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "copy-hover-display"))
        )

        # Locate the embed codes dropdown
        embed_dropdown_element = WebDriverWait(embed_codes_div, 10).until(
            EC.presence_of_element_located((By.ID, "uploaded-embed-toggle"))
        )
        embed_dropdown = Select(embed_dropdown_element)

        # Select "Direct links" from the dropdown
        embed_dropdown.select_by_visible_text(link_export_types)

        # Wait for the direct link textarea to become visible and get its value
        direct_link_textarea = WebDriverWait(embed_codes_div, 10).until(
            EC.visibility_of_element_located((By.XPATH, ".//div[@data-combo-value='direct-links']//textarea[@name='direct-links']"))
        )
        direct_link_text = direct_link_textarea.get_attribute("value")
        # Pretty print the direct links and save to file
        direct_links = direct_link_text.strip().split('\n')
        # logger.debug(f"Direct links to the uploaded images in album '{imgbb_album_id}':")
        output_json = {}
        for link in direct_links:
            stripped_link = link.strip()
            file_name = stripped_link.split("/")[-1]
            file_name = file_name.replace("-", ".")
            file_name = file_name.replace(".preview.webp", "_preview.webp")
            file_name = file_name.replace(".preview.sheet.webp", "_preview_sheet.webp")
            file_name = file_name.replace(".thumbnails.jpg", "_thumbnails.jpg")
            output_json[file_name] = stripped_link
            # logger.debug(f"{file_name}: {stripped_link}")

        with open(log_filename, 'w') as outfile:
            json.dump(output_json, outfile, indent=4)  # Save as pretty-printed JSON

        logger.info(f"Direct links saved to: {log_filename}")
        driver.quit()
        return True
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if 'driver' in locals() and driver is not None:
            driver.quit()
        return False


def process_files():
    # Load Config file
    config, exit_code = load_json_file("Config.json")
    if not config:
        exit(exit_code)

    working_path = config["working_path"]
    allowed_formats = config["allowed_formats"]
    ignored_files = config["ignored_files"]
    link_export_types = config["link_export_types"]
    headless_mode = config["headless_mode"]

    # Load Config file
    creds, exit_code = load_json_file("creds.secret")
    if not creds:
        exit(exit_code)

    imgbb_username = creds["imgbb_username"]
    imgbb_password = creds["imgbb_password"]
    imgbb_album_id = creds["imgbb_album_id"]
    ignored_files_lower = {name.lower() for name in ignored_files}

    file_list = [
        f for f in Path(working_path).iterdir()
        if f.is_file() and f.suffix.lower() in allowed_formats and f.name.lower() not in ignored_files_lower
    ]
    # for f in Path(working_path).iterdir():
    #     if f.is_file():
    #         logger.debug(f"- {f.name.lower()}")

    # Timestamp based filename:
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # log_filename = Path(working_path) / f"direct_links_{timestamp}.txt"

    # Folder based filename
    working_path_obj = Path(working_path)
    folder_name = working_path_obj.name
    log_filename = working_path_obj / f"{folder_name}_imgbb.txt"

    # Check if the imgbb file exists and delete it
    if os.path.exists(log_filename):
        os.remove(log_filename)

    result = upload_to_imgbb(headless_mode, imgbb_username, imgbb_password, imgbb_album_id, working_path, file_list, link_export_types, log_filename)

    if result:
        logger.success(f"Upload has been completed for path: {working_path}")
    else:
        logger.error(f"Upload failed for path: {working_path}")


if __name__ == "__main__":
    # Add Logger to file
    logger.add("App_Log_{time:YYYY.MMMM}.log", rotation="30 days", backtrace=True, enqueue=False, catch=True)  # Load Logger
    process_files()




