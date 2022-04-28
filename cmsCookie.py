from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
import re

username="username"
password="password"

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

driver.get("https://cms.sic.saarland/system/users/login")
driver.find_element_by_xpath('//*[@id="UserUsername"]').send_keys(username)
driver.find_element_by_xpath('//*[@id="UserPassword"]').send_keys(password)
driver.find_element_by_xpath('/html/body/div[1]/div[1]/form/button').click()

WebDriverWait(driver=driver, timeout=10).until(
    lambda x: x.execute_script("return document.readyState === 'complete'")
)

with open ('cmsCookie.txt', 'w' ) as f:
	f.write("cms.sic.saarland\tFALSE\t/\tTRUE\t" + str(driver.get_cookie('CakeCMS')['expiry']) + "\tCakeCMS\t" + driver.get_cookie('CakeCMS')['value'])
