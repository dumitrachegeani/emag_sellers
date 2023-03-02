import csv
import time
import re

import selenium
import windscribe

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


def change_vpn():
    windscribe.connect(rand=True)


all_vendors = []


def extract_vendors():
    vendors_div = driver\
        .find_element(By.CSS_SELECTOR, 'div[data-name="Livrat de"]')

    try:
        more_vendors_button = vendors_div\
            .find_element(By.CSS_SELECTOR, 'a.filter-extra-options-btn.js-toggle-filter-extra-options')
        more_vendors_button.click()

        vendors_popup_locator = (By.CSS_SELECTOR,
                                 'div.filter.filter-default.js-filter[data-filter-id="6427"][data-filter-group="true"][data-choice-type="multiple"][data-type="vendor"]')
        vendors_popup = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(vendors_popup_locator))

        elements = vendors_popup.find_elements(By.CSS_SELECTOR, 'a.js-filter-item.filter-item.text-truncate.col-sm-4')
    except:
        vendors = vendors_div.find_elements(By.TAG_NAME, 'a')
        elements = [vendor for vendor in vendors if vendor.text != 'Livrat de' and vendor.text.strip() != '']



    all_vendors.extend(elements)

    if len(all_vendors) > 200:
        write_to_csv_elements(all_vendors, 'vendors.csv')
        all_vendors.clear()


def extract_brands():
    brands_div = driver.find_element(By.CSS_SELECTOR, 'div[data-name="Brand"]')
    brands = brands_div.find_elements(By.TAG_NAME, 'a')
    filtered_brands = [brand for brand in brands if brand.text != 'Brand' and brand.text.strip() != '']
    write_to_csv_elements(filtered_brands, 'brands.csv')


def write_to_csv_elements(elements, filename='example.csv'):
    with open(filename, 'a+', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        row = []
        for i, element in enumerate(elements):
            text = re.sub(r'\s*\(\d+\)', '', element.text)
            row.append(text)
            if (i + 1) % 50 == 0:  # Write 50 elements per row
                writer.writerow(row)
                row = []
        if row:  # Write any remaining elements
            writer.writerow(row)
        file.flush()

if __name__ == '__main__':
    windscribe.login('geanyhalav', 'croco2001')

    change_vpn()

    # open the driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.delete_all_cookies()

    categories = []
    with open("links.txt") as file:
        for line in file:
            categories.append(line.strip())
    categorie_names = []

    max_attempts = 3
    for category_link in categories:
        attempts = 0
        while max_attempts > attempts:  # repeat until a break statement is executed
            attempts += 1
            try:
                print('Scrapping ', category_link)
                driver.get(category_link)

                # extract category name
                category = category_link.split('/')[-2]  # get the second last element after splitting by '/'
                category = category.replace("_", " ").replace("-", " ").replace("%", " ")
                categorie_names.append(category)

                start = time.time_ns()
                try:
                    extract_vendors()
                    end = time.time_ns()
                    print('extracted vendors in ', (end - start) / 1_000_000_000, 'seconds')
                except NoSuchElementException as e:
                    raise NoSuchElementException
                except Exception as e:
                    print('Vendors are not availabe\n', e)

                start = time.time_ns()
                extract_brands()
                end = time.time_ns()
                print('extracted brands in ', (end - start) / 1_000_000_000, 'seconds')

                change_vpn()
                break
            except NoSuchElementException as e:
                print("Element not found. Retrying...", e)
                print('category completed: ', categories.index(category_link))
                change_vpn()
                continue
            except Exception as e:
                print('category completed: ', categories.index(category_link))
                continue

    with open('categories.csv', 'a+', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        writer.writerow(categorie_names)
