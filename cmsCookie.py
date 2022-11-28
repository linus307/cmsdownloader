#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re, secretstorage

connection = secretstorage.dbus_init()
collection = secretstorage.get_default_collection(connection)

username = ""
password = [x for x in collection.search_items({'name':'cms_password'})][0].get_secret().decode('utf-8')

connection.close()

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get("https://cms.sic.saarland/system/users/login")
driver.find_element("xpath", '//*[@id="UserUsername"]').send_keys(username)
driver.find_element("xpath", '//*[@id="UserPassword"]').send_keys(password)
driver.find_element("xpath", '/html/body/div[1]/div[1]/form/button').click()

WebDriverWait(driver=driver, timeout=10).until(
    lambda x: x.execute_script("return document.readyState === 'complete'")
)

with open ('cmsCookie.txt', 'w' ) as f:
	f.write("cms.sic.saarland\tFALSE\t/\tTRUE\t" + str(driver.get_cookie('CakeCMS')['expiry']) + "\tCakeCMS\t" + driver.get_cookie('CakeCMS')['value'])
