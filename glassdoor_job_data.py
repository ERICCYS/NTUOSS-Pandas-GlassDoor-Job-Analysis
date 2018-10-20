from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException

import scrapy
from scrapy import spider
from scrapy.spiders import CrawlSpider, Rule

import csv
import json
import re
import requests
import time

driver = webdriver.Chrome(executable_path='C:\\Users\\Eric\\Desktop\\chromedriver')
driver.get("https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=&sc.keyword=&locT=C&locId=3235921&jobType=")

# This is an example to clone the Software Engineer Job
# Iterate though all the jobs like below will be a bit inefficient, cos we can copy this scrpit for each job and let them crawling data concurrently.
jobs = ['Software Engineer', 'Data Scientist', 'Developer', 'UI Designer', 'Cyber Security']
csv_file = open('Software Engineer.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Job Title', 'Company', 'Salary 50th Percentile', 'Salary 10th Percentile', 'Salary 90th Percentile', 'Overall Rating', 'Comapny Description', 'Founded Year', 'Head Quarter', 'Company Size', 'Industry', 'Company Revenue', 'Job Description'])

# for keyword in jobs:
jobname = driver.find_element_by_name('sc.keyword')
jobname.clear()
keyword = jobs[0]
jobname.send_keys(keyword)

driver.find_element_by_xpath('//*[@id="SiteSrchTop"]/form/button').click()
time.sleep(3)

# Make http requests to get the detialed infrmation of each job
url = 'https://www.glassdoor.com/Job/json/details.htm'
headers = {
            'cache-control': "no-cache",
            'Postman-Token': "df9cc79f-2b27-4731-9402-b4485f485d06",
            'user-agent': "OPEN SOURCE"
          }

page_to_crawl = 100
for i in range(page_to_crawl):
    try:
        for ele in driver.find_elements_by_xpath('//*[@id="MainCol"]/div/ul/li'):
            title = ele.find_element_by_xpath('./div[2]/div[1]/div[1]/a').text
            link = ele.find_element_by_xpath('./div[2]/div[1]/div[1]/a').get_attribute('href')
            company = ele.find_element_by_xpath('./div[2]/div[2]/div[1]').text[:-12]
            print(title)
            print(company)
            first_split = link.split('?')
            parameters = first_split[1]
            second_split = parameters.split('&')
            querystring = {}
            for param in second_split :
                param = param.split('=')
                querystring[param[0]] = param[1]

            response = requests.get(url, headers=headers, params=querystring)
            info = json.loads(response.text)

            # Salary related:
            salaryP50 = None
            salaryP10 = None
            salaryP90 = None
            try:
                company_salaries = info['salary']['salaries']
                for company_salary in company_salaries:
                    if company_salary['jobTitle'] == title or company_salary['jobTitle'] == keyword or keyword in company_salary['jobTitle']:
                        try:
                            salaryP50 = company_salary['salaryPercentileMap']['payPercentile50']
                        except (IndexError, KeyError) as e:
                            pass

                        try:
                            salaryP10 = company_salary['salaryPercentileMap']['payPercentile10']
                        except (IndexError, KeyError) as e:
                            pass

                        try:
                            salaryP90 = company_salary['salaryPercentileMap']['payPercentile90']
                        except (IndexError, KeyError) as e:
                            pass
                        break
            except (IndexError, KeyError) as e:
                pass

            # Company information related:
            overall_rating = None
            company_description = None
            company_found_year = None
            company_hq = None
            company_size = None
            company_industry = None
            company_revenue = None

            try:
                overall_rating = info['rating']['starRating']
            except (IndexError, KeyError) as e:
                 pass

            try:
                company_description = info['overview']['description']
            except (IndexError, KeyError) as e:
                pass

            try:
                company_found_year = info['overview']['foundedYear']
            except (IndexError, KeyError) as e:
                pass

            try:
                company_hq = info['overview']['hq']
            except (IndexError, KeyError) as e:
                pass

            try:
                company_size = info['overview']['size']
            except (IndexError, KeyError) as e:
                pass
            if company_size == 'Unknown':
                company_size = None

            try:
                company_industry = info['overview']['industry']
            except (IndexError, KeyError) as e:
                pass

            try:
                company_revenue = info['overview']['revenue']
            except (IndexError, KeyError) as e:
                pass
            if company_revenue == 'Unknown / Non-Applicable':
                company_revenue = None

            # Infomation related to job
            job_description = None
            try:
                job_description_string = info['job']['description']
                job_description_string.replace('\n', '')
                job_description_elements = job_description_string.split("<br/><br/>")
                if job_description_elements != None:
                    job_description = ''
                for job_description_element in job_description_elements:
                    job_description_element.replace('\n', '')
                    processed_job_description_element = re.sub(r'<\\*.>', ' ', job_description_element)
                    processed_job_description_element = re.sub(r'<.*>', '', processed_job_description_element)
                    processed_job_description_element = re.sub('[^a-zA-Z0-9-_+~?<>;=%$&!\'\",/()#@*.]', ' ', processed_job_description_element)
                    job_description += processed_job_description_element
            except (IndexError, KeyError) as e:
                 pass

            try:
                csv_writer.writerow([title, company, salaryP50, salaryP10, salaryP90, overall_rating, company_description, company_found_year, company_hq, company_size, company_industry, company_revenue, job_description])
            except UnicodeError:
                pass
            time.sleep(2)

        try:
            driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click()
        except WebDriverException:
            driver.find_element_by_xpath('//*[@id="JAModal"]/div/div[2]/div[1]').click()
            driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click()

    except NoSuchElementException or WebDriverException:
        try:
            driver.find_element_by_xpath('//*[@id="JAModal"]/div/div[2]/div').click()
        except NoSuchElementException:
            print ("Finished %s"%keyword)
    time.sleep(2)

csv_file.close()
