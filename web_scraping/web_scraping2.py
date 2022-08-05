# python -m pip install lxml
# Python -m pip install beautifulsoup4

# TODO: Get if in stock for each type

from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
import requests, os
from selenium import webdriver
from selenium.webdriver.support.ui import Select


# for a in soup.findAll('a',href=True,attrs={'class':'buyPriceInner'}):
# name=a.find('div', attrs={'class':'_3wU53n'})
# price=a.find('div', attrs={'class':'buyPriceInner'})
# rating=a.find('div', attrs={'class':'hGSR34 _2beYZw'})
# products.append(name.text)
# prices.append(price.text)
# ratings.append(rating.text)

##RADWELL
def getRadwellPrice(part):  # TODO: Get how many in stock
    line = getLine(part)
    url = f"https://www.radwell.com/en-US/Buy/{line}/{line}/{part}/"

    status, content = checkRequestStatus(url)

    if status == 200:
        soup = BeautifulSoup(content, features="lxml")

        prices = [None,None,None,None,None]
        stocks = [None,None,None,None,None]

        k = 0

        # In stock
        for i in soup.find_all(class_='buyOpt active'):
            try:

                text = i.find(class_='buyCond conditionPopupOpener').text
                found = False
                if "Radwell Independent" in text:
                    index = 3
                    found = True
                elif "Surplus Never Used Original" in text:
                    index = 0
                    found = True
                elif "Surplus Never Used Radwell" in text:
                    index = 1
                    found = True
                elif "Previously Used" in text:
                    index = 2
                    found = True

                ##stocks.append([])
                if found:
                    #prices.append(i.find(class_="buyPriceInner").text[2:].replace(",", ""))
                    prices[index] = getPrice(i.find(class_="buyPriceInner").text)

                    try:
                        stock = i.find(class_='stock instock').text
                        #stock = stock[4:]

                        sum = ""
                        for let in stock:
                            if let == " ":
                                try:
                                    stocks[index] = str(int(sum))
                                    break
                                except:
                                    sum = ""
                            else:
                                sum += let
                    except:
                        stocks[index] = 0

                    k+=1
            except Exception as e:
                print(e,k)
                ##k+=1

        # Not in stock
        for i in soup.find_all(class_='buyOpt nostock active'):  # Means in stock
            try:
                found = False

                text = i.find(class_='buyCond conditionPopupOpener').text
                if "Radwell Independent" in text:
                    index = 3
                    found = True
                elif "Surplus Never Used Original" in text:
                    index = 0
                    found = True
                elif "Surplus Never Used Radwell" in text:
                    index = 1
                    found = True
                elif "Previously Used" in text:
                    index = 2
                    found = True
                elif "repair" in text:
                    index = 4
                    found = True
                ##stocks.append([])
                if found:
                    #prices.append(i.find(class_="buyPriceInner").text[2:].replace(",", ""))
                    prices[index] = getPrice(i.find(class_="buyPriceInner").text)

                    stocks[index] = 0

                    k+=1
            except Exception as e:
                ##k+=1
                print(e,k)

        #Repair Price
        for i in soup.find_all(class_='repPrice'):
            prices[4] = getPrice(i.text)
            stocks[4] = 0

        # prices = []
        # types = []

        ##prices
        # for div in soup.find_all('span',class_ = 'buyPriceInner'):
        # prices.append(div.text[2:]) #deletes dollar sign

        ##type
        # for h3 in soup.find_all('h3',class_='buyCond conditionPopupOpener'):
        # text = h3.text
        # if "Radwell Independent Supply Chain" in text:
        # types.append("New")
        # elif "Surplus Never Used Original" in text:
        # types.append("New")
        # elif "Surplus Never Used Radwell" in text:
        # types.append("New No Box")
        # elif "Previously Used" in text:
        # types.append("Refurbished")

        return prices, stocks


##APEXPLC
def getApexPLCPrice(part):
    url = f"https://www.apexplc.com/products/{part}"

    status, content = checkRequestStatus(url)

    if status == 200:
        soup = BeautifulSoup(content, features="lxml")

        prices = [None, None, None, None, None]
        stocks = [None, None, None, None, None]
        types = [None, None, None, None, None]

        ##prices
        for dev in soup.find_all('option'):
            price = ''
            for i in dev.text[::-1]:
                if i != " ":
                    price += i
                else:
                    break

            for type,index in zip(["New Opened Box", "New No Box", "New", "Refurbished"],[4,1,0,2]):
                if type in dev.text:
                    types[index] = type
                    prices[index] = price[::-1]
                    break

            # first one New, second Refurbished
            # or New, New Opened Box, New No Box, Refurbished


        ##Get stock
        #for option in soup.find_all("option"):
            #print(option["value"])
        ##THEN USE the options to get page variants. CAN'T USE REQUESTS - Gets same page source for each option. Have use Selenium to get current text
        #url = "https://www.apexplc.com/products/ms-fec2611-0?variant=1434349240341"

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument(str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver.exe")))

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        select = Select(driver.find_element_by_id("product-variants-option-0"))

        for i in range(len(types)):
            if types[i] is not None:
                select.select_by_visible_text(types[i])
                element = driver.find_element_by_id("variant-inventory")
                # element = driver.find_element_by_css_selector("h3")
                text = element.get_attribute('innerHTML')

                if "We have" in text: #If in stock, comment starts with "We have"
                    text = text[4:]

                    t = ""
                    for let in text:
                        if let == " ":
                            try:
                                stocks[i] = str(int(t))
                                break
                            except:
                                t = ""
                        else:
                            t += let
                elif "Please call" in text: #If not in stock, comment starts with "Please call"
                    stocks[i] = 0
        driver.close()

        return prices, stocks, types

def getIndustrialAutomationsPrice(part):
    line = getLine(part)

    url = f"https://industrialautomationco.com/collections/{line}/products/{part}"

    status, content = checkRequestStatus(url)

    if status == 200:
        soup = BeautifulSoup(content, features="lxml")

        ##prices
        prices = []
        types = []
        for dev in soup.find_all('option'):
            pass

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument(str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver.exe")))

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        select = Select(driver.find_element_by_id("SingleOptionSelector-0")) # I believe this is the correct id selector
        select.select_by_visible_text("New Surplus")
        select.select_by_visible_text("Refurbished")
        element = driver.find_element_by_class_name("price__regular")
        text = element.get_attribute('innerHTML')
        print(getPrice(text))


# def getPLCUnlimitedPrice(part):
# url = f""

def checkRequestStatus(url):
    resp = requests.get(url)
    status = resp.status_code

    if status == 404:
        print("Website could not be found")
        return status, ""
    else:
        return status, resp.text

def getLine(part):
    ind = part[0].lower()

    if ind in ["c","r"]:
        line = "Omron"
    elif ind in ["f","a","q","h"]:
        line = "Mitsubishi"
    elif ind in ["n","a"]:
        line = "johnson-controls"
    elif ind == "m":
        if part[0:2].lower() == "ms":
            line = "johnson controls"
        else:
            line = "mitsubishi"
    else:
        line = ""
    try:
        int(ind)
        line = "Allen-Bradley"
    except:
        pass
    #TODO: SICK, Johnson controls has m and n parts
    return line

def getPrice(string):
    price = ""
    for s in string:
        try:
            price += str(int(s))
        except:
            pass

    #insert decimal
    price = price[:-2] + "." + price[-2:]

    return "{:,.2f}".format(float(price))

#print(getIndustrialAutomationsPrice("2094-BC02-M02-M"))
#print(getRadwellPrice("ms-fec2611-0"))
print(getApexPLCPrice("ms-fec2611-0"))