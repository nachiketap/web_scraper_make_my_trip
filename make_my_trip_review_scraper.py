#importing the libraries

import pandas as pd #data analysis

from bs4 import BeautifulSoup #web scraper/data parser

import selenium.webdriver #Browser automation
from selenium.webdriver.support.ui import WebDriverWait #Browser automation
from selenium.webdriver.common.keys import Keys #Browser automation

import time

#defining the review parser function

def review_parser(baseDataUrl):
    driver = selenium.webdriver.Chrome(r"C:\Users\Nachiketa\Downloads\chromedriver_win32\chromedriver.exe") #Change URL accordingly
    driver.get(baseDataUrl) #Opening the base data URL
    time.sleep(5)
    driver.maximize_window()

    name = driver.find_element_by_xpath('//*[@id="detpg_hotel_name"]').text #name of the hotel
    #print(name)

    try:
        driver.find_elements_by_xpath('//*[@id="detpg_user_reviews"]')[0].click() #navigate to rating and reviews
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight") #evaluate the height of the webpage
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #scroll to the bottom

        driver.find_elements_by_xpath('//*[@id="detpg_review_ratings_pagination"]/ul/li[9]/a')[0].click() #navigate to the last page
        pages = int(driver.find_element_by_xpath('//*[@id="detpg_review_ratings_pagination"]/ul/li[7]/a').text) #number of pages
        driver.find_elements_by_xpath('//*[@id="detpg_review_ratings_pagination"]/ul/li[1]/a')[0].click() #navigate back to the first page

        df = [["Review Date", "Review"]]
        rating = []

        for i in range(pages):
            body = driver.find_element_by_tag_name("body").get_attribute("innerHTML")
            body = BeautifulSoup(body) # Parse the inner HTML using BeautifulSoup

            review_date = body.findAll("p", {"class": "grayText appendBottom10"}) #tags for guest name and date of review
            review = body.findAll("p", {"class": "font14 lineHight22"}) #tags for the guest review
            tags = body.findAll("div", {"class": "reviewRow"}) #tags for ratings
            for tag in tags:
                score = tag.find("span")
                rating.append(score.text)
    
            for j in range(0, len(review_date)):
                df.append([review_date[j].text, review[j].text])
    
            driver.find_elements_by_xpath('//*[@id="detpg_review_ratings_pagination"]/ul/li[8]/a')[0].click() #navigate to the next page
            time.sleep(2)

        driver.close() #quit the browser
    
        data = pd.DataFrame(df, columns = df[0]).drop(0)
        data["Rating"] = rating
        data["Hotel Name"] = name
        return data
    except:
        driver.close() #quit the browser

#extracting the URLs for all the hotels in the area

baseDataUrl = "https://www.makemytrip.com/hotels/hotel-listing/?checkin=08282020&checkout=08292020&locusId=CTGOI&locusType=city&city=CTGOI&country=IN&searchText=Goa%2C%20India&roomStayQualifier=2e0e&_uCurrency=INR&reference=hotel&type=city"
driver = selenium.webdriver.Chrome(r"C:\Users\Nachiketa\Downloads\chromedriver_win32\chromedriver.exe")
driver.get(baseDataUrl) #opening the base data URL
time.sleep(5) #wait for the webpage to load

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #scroll down to bottom
    time.sleep(5) #wait to load page
    new_height = driver.execute_script("return document.body.scrollHeight") #calculate new scroll height and compare with last scroll height
    if new_height == last_height:
        break
    last_height = new_height
    
driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME) #scroll up
time.sleep(2)

body = driver.find_element_by_tag_name("body").get_attribute("innerHTML")
body = BeautifulSoup(body) # Parse the inner HTML using BeautifulSoup

outerrow = body.findAll("div", {"class": "listingRowOuter"})
#print(len(outerrow)) #number of hotels in the area

urls = []
for row in outerrow:
    url = row.find("a")
    urls.append(url['href'])
#print(len(urls))

#fucntion to prepend the string 'https:' to the extracted URLS

def prepend(list, str):  
    str += '{0}'
    list = [str.format(i) for i in list] 
    return(list) 

string = 'https:'
urls = prepend(urls, string)

#scraping the reviews

data = pd.DataFrame(columns = ["Review Date", "Review", "Rating", "Hotel Name"])
for url in urls:
    df = review_parser(url)
    data = pd.concat([data, df])

#data.to_csv(index = False)