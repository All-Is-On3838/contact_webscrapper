## for automated extraction, creation of csv, and email of NASEN contact information
## Created by Allison Li 2023-07-16
## Modified by...


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import logging

#import modules
from check_changes import *
from send_email import *

def convert_filetime(dateString):
    date_time_obj = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S.%f')
    return date_time_obj.strftime("%Y_%m_%d_%H_%M")

class scrapper():
    def __init__(self):
        # set chromedriver options
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-default-apps')
        options.add_argument('--no-sandbox') # required to run in docker
        options.add_argument('--headless') # don't need to open window
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('log-level=3')

        # Configure webdriver
        self.driver = webdriver.Chrome(options=options)

        # Open the website
        self.driver.get('https://nasen.org/')

    def pass_about_us(self):
        # Click past "about us" screen
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def get_sites(self):
        # Find all the links on the page
        rows = self.driver.find_elements(By.CSS_SELECTOR, '.clickable-row')

        # Store the extracted data
        data = []

        # Extract the "data-href" attribute value and text from each row
        for row in rows:
            data_href = row.get_attribute('data-href')
            name_col_text = row.find_element(By.CLASS_NAME, 'nameCol').text.strip()

            # Create a dictionary for each row and append it to the data list
            row_data = {
                'link': '',
                'site': '',
                'addresses': '',
                'emails': [],
                'phones': [],
                'services': [],
                'websites': []
            }

            try:
                row_data['link'] = data_href
            except:
                logger.exception(f'unable to assign {data_href} to link key')

            try:
                row_data['site'] = name_col_text
            except:
                logger.exception(f'unable to assign {name_col_text} to site key')

            try:
                data.append(row_data)
            except:
                logger.exception('unable to append row_data to data')

        return data

    def get_site_info(self, data):
        # Loop through each link
        for item in data:
            
            # Get the URL of the link
            base_site = 'https://nasen.org'
            link = item['link']
            url_errors = []
            try:
                url = f'{base_site}{link}'
            except:
                url_errors.append(url)

            # If the link doesn't have a valid URL, skip it
            if not url or 'javascript' in url:
                continue
            
            # Open the link
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(url)
            
            # Wait for the page to load
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                # Get site name
                try:
                    site_name = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
                    if site_name == "404 Error":
                        continue
                    else:
                        item['site'] = site_name
                        
                except Exception as e:
                    logger.exception(f"Unable to confirm site name for {item['site']}: {str(e)}")

                # Get address
                try:
                    site_address = self.driver.find_element(By.CSS_SELECTOR, '.span3 > p:nth-child(2)').text.strip()
                    site_address = site_address.replace('<br>', ' ') # Remove <br>
                    site_address = site_address.replace('\n', ' ') # Format address to be on one line
                    item['addresses'] = site_address
                except Exception as e:
                    logger.exception(f"Unable to get address for {item['site']}: {str(e)}")

                # Get email(s)
                try:
                    email_elements = self.driver.find_elements(By.XPATH, '//a[starts-with(@href, "mailto:")]')
                    for element in email_elements:
                        email = element.text
                        item['emails'].append(email)
                except Exception as e:
                    logger.exception(f"Unable to get emails for {item['site']}: {str(e)}")

                # Get phone number(s)
                try:
                    phone_elements = self.driver.find_elements(By.XPATH, '//a[starts-with(@href, "tel:")]')
                    for element in phone_elements:
                        phone = element.text
                        if phone != '(253) 272-4857':
                            item['phones'].append(phone)
                except Exception as e:
                    logger.exception(f"Unable to get phone numbers for {item['site']}: {str(e)}")

                # Get websites
                try:
                    url_elements = self.driver.find_elements(By.XPATH, '//*[@id="slide2"]/div/div[3]/div[3]/p[4]/a')
                    for element in url_elements:
                        url = element.text
                        item['websites'].append(url)
                except Exception as e:
                    logger.exception(f"Unable to get websites for {item['site']}: {str(e)}")

                # Get services
                try:
                    # Find the <ul> element containing the list
                    ul_element = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Services')]/following-sibling::ul")

                    # Find all <li> elements within the <ul> element
                    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

                    # Extract the text from each <li> element and store it in a list
                    service_list = [li.text for li in li_elements]

                    # Append list to dictionary
                    item['services'] = service_list
                except Exception as e:
                    logger.exception(f"Unable to get services for {item['site']}: {str(e)}")

            except TimeoutException:
                logger.exception('Page timed out:', url)
            except Exception as e:
                logger.exception("Issue with webdriver accessing site page: {str(e)}")
            finally:
                # Close the current tab and switch back to the main tab
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

        return data

    def teardown(self):
        # Close the web driver
        self.driver.quit()

if __name__ == "__main__" :
# Start the timer
    timer = time.time() # time as floating-point number for calculation
    start_time = convert_filetime(str(datetime.now())) # time as datetime object for formatting

# Set up logger
    logger = logging.getLogger(__name__) 
    logger.setLevel(logging.DEBUG) 

    filehandler_name = f"logs/{start_time}_NASEN_Contact_Extraction.log"
    formatter = logging.Formatter('%(levelname)s %(filename)s %(asctime)s %(message)s')
    filehandler = logging.FileHandler(filename=filehandler_name)
    filehandler.setFormatter(formatter)

    logger.addHandler(filehandler)

    logger.info('***************************************')
    logger.info('New Program Run for NASEN Contact Update')
    logger.info("Process started at: " + start_time)
    logger.info('***************************************')

# Scrape website for data
    # Initalize scrapper
    scrapper = scrapper()

    # Get sites
    scrapper.pass_about_us()
    data = scrapper.get_sites()
        
    # Get site info
    data = scrapper.get_site_info(data)

    # Exit session
    scrapper.teardown()

# Check data for changes
    # Set up variables for check change functions
    result = []

    master_file_path = 'results/nasen_contact_info_master.csv'
    masterfile= csv_to_dict(master_file_path)

    column_values = masterfile[0].keys()

    # Compare each item in masterfile with data
    compare_files(masterfile, data, column_values, result)

    # Find new items in data
    check_new_sites(masterfile, data, column_values, result)

    # Create csv with result
    result_path = f"results/NASEN_contact_updates_{start_time}.csv"
    dict_to_csv(result, result_path)

    # Email result csv
    send_email(result_path)

    # Update masterfile with changes
    update_masterfile(masterfile, result)

    # Update master csv with changes
    dict_to_csv(masterfile, master_file_path)
        
    # Calculate the elapsed time
    elapsed_time = time.time() - timer

    # Print the elapsed time
    logger.info('***************************************')
    logger.info("Run complete.")
    logger.info("Elapsed time: {:.2f} seconds".format(elapsed_time))
    logger.info('***************************************')
