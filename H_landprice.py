from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from fake_useragent import UserAgent 
import time,random
import requests
from bs4 import BeautifulSoup as bs
import re
import ddddocr
import pandas as pd

error = []
chrome_driver_path = "/home/yeshome/桌面/爬蟲/chromedriver"
house_href = []
ua = UserAgent()
options = Options() 
options.add_argument('--headless') 
options.add_argument("user-agent=" + ua.chrome)
driver = webdriver.Chrome(chrome_driver_path, options=options)
driver = webdriver.Chrome(chrome_driver_path)
driver.implicitly_wait(10)
url = "https://www.land.tycg.gov.tw/chaspx/SQry1.aspx/517"
driver.get(url)

time.sleep(random.uniform(2, 4))

driver.switch_to.frame(driver.find_element(By.XPATH,'/html/body/form/div[4]/div[3]/div/div/div[2]/iframe'))

xcity_select = Select(driver.find_element(By.XPATH, '//*[@id="xcity"]'))
xcity_options = [option.get_attribute("value") for option in xcity_select.options]
xcity_options.pop(0)

print(xcity_options)

print('已抓取所有行政區')


for xcity_option in xcity_options:
    xcity_select = Select(driver.find_element(By.XPATH, '//*[@id="xcity"]'))
    xcity_select.select_by_value(xcity_option)
    print('目前正在抓取行政區' + xcity_option)
    time.sleep(random.uniform(2, 5))
    xarea_select = Select(driver.find_element(By.ID, 'xarea'))
    xarea_options = [option.get_attribute("value") for option in xarea_select.options]
    xarea_options.pop(0)
    print('已抓取所有段別')
    for xarea_option in xarea_options:
        try:
            print('目前正在抓取行政區' + xcity_option + '段別' + xarea_option)
            xcity_select = Select(driver.find_element(By.XPATH, '//*[@id="xcity"]'))
            xcity_select.select_by_value(xcity_option)
            time.sleep(random.uniform(3, 5))

            xarea_select = Select(driver.find_element(By.ID, 'xarea'))
            xarea_select.select_by_value(xarea_option)
            time.sleep(random.uniform(3, 5))
            
            input_num = driver.find_element(By.XPATH, '/html/body/form/div[4]/table/tbody/tr[6]/td/input')
            input_num.clear()
            input_num.send_keys('9999')
            
            img_element = driver.find_element(By.XPATH, '/html/body/form/div[4]/table/tbody/tr[7]/td/img')
            screenshot = img_element.screenshot_as_png

            with open("認證碼.png", "wb") as file:
                file.write(screenshot)

            ocr = ddddocr.DdddOcr()
            with open('認證碼.png', 'rb') as f:
                img_bytes = f.read()
            check_code = ocr.classification(img_bytes)

            check = driver.find_element(By.XPATH, '//*[@id="checkno"]')
            check.clear()
            check.send_keys(check_code)
            time.sleep(random.uniform(3, 5))

            search = driver.find_element(By.XPATH,'//*[@id="btnSearch2"]')
            search.click()
            
            time.sleep(random.uniform(2, 4))

            table = pd.read_html(driver.page_source, attrs={"id": "GridView6"})

            print(table)

            df = table[0]

            df2 = pd.DataFrame()
            df2['lkey'] = 'H_' + xcity_option + '_' + xarea_option + '_' + df['地號']
            df2['land_area_size'] = df['面積'].apply(lambda x: float(re.findall(r'\d+\.\d+|\d+', x.replace(',', ''))[0]) if isinstance(x, str) else "--")
            df2['clv'] = df['當期公告現值'].apply(lambda x: re.findall(r'\d+', x.replace(',', ''))[0] if isinstance(x, str) else "--")
            df2['alv'] = df['公告地價'].apply(lambda x: re.findall(r'\d+', x.replace(',', ''))[0] if isinstance(x, str) else "--")


            csv_filename = '/home/yeshome/桌面/爬蟲/桃園/H_{}_{}.csv'.format(xcity_option, xarea_option)
            df2.to_csv(csv_filename, index=False)

            print('已導出CSV檔')

            time.sleep(random.uniform(1, 3))

            driver.get(url)

            time.sleep(random.uniform(2, 4))

            driver.switch_to.frame(driver.find_element(By.XPATH,'/html/body/form/div[4]/div[3]/div/div/div[2]/iframe'))
        except:
            error.append('行政區' + xcity_option + '段別' + xarea_option)
            print('錯誤:行政區' + xcity_option + '段別' + xarea_option)

print('已爬完')
print(error)




