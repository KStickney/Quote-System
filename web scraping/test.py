#python -m pip install lxml
#Python -m pip install beautifulsoup4

#TODO: Get if in stock for each type

from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
import requests

#for a in soup.findAll('a',href=True,attrs={'class':'buyPriceInner'}):
    #name=a.find('div', attrs={'class':'_3wU53n'})
    #price=a.find('div', attrs={'class':'buyPriceInner'})
    #rating=a.find('div', attrs={'class':'hGSR34 _2beYZw'})
    #products.append(name.text)
    #prices.append(price.text)
    #ratings.append(rating.text)

##RADWELL
def getRadwellPrice(line,part): #TODO: Get how many in stock
    url = f"https://www.radwell.com/en-US/Buy/{line}/{line}/{part}/"

    status, content = checkRequestStatus(url)

    if status == 200:
        soup = BeautifulSoup(content, features="lxml")

        prices = []
        types = []
        stocks = []

        #In stock
        for i in soup.find_all(class_ = 'buyOpt active'):
            try:
                prices.append(i.find(class_="buyPriceInner").text[2:].replace(",",""))

                text = i.find(class_='buyCond conditionPopupOpener').text
                if "Radwell Independent Supply Chain" in text:
                    types.append("New")
                elif "Surplus Never Used Original" in text:
                    types.append("New")
                elif "Surplus Never Used Radwell" in text:
                    types.append("New No Box")
                elif "Previously Used" in text:
                    types.append("Refurbished")

                stocks.append("In Stock")
            except:
                pass

        #Not in stock
        for i in soup.find_all(class_ = 'buyOpt nostock active'): #Means in stock
            try:
                prices.append(i.find(class_="buyPriceInner").text[2:].replace(",",""))

                text = i.find(class_='buyCond conditionPopupOpener').text
                if "Radwell Independent Supply Chain" in text:
                    types.append("New")
                elif "Surplus Never Used Original" in text:
                    types.append("New")
                elif "Surplus Never Used Radwell" in text:
                    types.append("New No Box")
                elif "Previously Used" in text:
                    types.append("Refurbished")

                stocks.append("Out Of Stock")
            except:
                pass

        #prices = []
        #types = []

        ##prices
        #for div in soup.find_all('span',class_ = 'buyPriceInner'):
            #prices.append(div.text[2:]) #deletes dollar sign

        ##type
        #for h3 in soup.find_all('h3',class_='buyCond conditionPopupOpener'):
            #text = h3.text
            #if "Radwell Independent Supply Chain" in text:
                #types.append("New")
            #elif "Surplus Never Used Original" in text:
                #types.append("New")
            #elif "Surplus Never Used Radwell" in text:
                #types.append("New No Box")
            #elif "Previously Used" in text:
                #types.append("Refurbished")

        return prices, types, stocks

##APEXPLC
def getApexPLCPrice(part):
    url = f"https://www.apexplc.com/products/{part}"

    status,content = checkRequestStatus(url)

    if status == 200:
        soup = BeautifulSoup(content, features="lxml")
        print(soup)
        ##prices
        prices = []
        types = []
        for dev in soup.find_all('option'):
            price = ''
            for i in dev.text[::-1]:
                if i != " ":
                    price += i
                else:
                    break

            prices.append(price[::-1])

            for type in ["New Opened Box","New No Box","New","Refurbished"]:
                if type in dev.text:
                    types.append(type)
                    break

            #first one New, second Refurbished
            #or New, New Opened Box, New No Box, Refurbished

        stocks = [] #TODO: to get different prices, have to use selenium to select different dropdown items
        for stock in soup("link",itemprop="availability"): #Todo: what do for if one version in stock but others aren't
            text = str(stock['href'])
            if "Stock" in text:
                if "In" in text:
                    stocks.append("In Stock")
                elif "Out" in text:
                    stocks.append("Out of Stock")

        return prices, types

#def getPLCUnlimitedPrice(part):
    #url = f""

def checkRequestStatus(url):
    resp = requests.get(url)
    status = resp.status_code

    if status == 404:
        print("Website could not be found")
        return status,""
    else:
        return status,resp.text

payload = {
    "product-variants-option-0":"Refurbished"
}

url = "https://www.apexplc.com/products/ms-fec2611-0"
r = requests.post(url,payload)
print(r.text)
print(r.status_code)