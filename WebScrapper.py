import requests
import pandas as pd
import json

#https://financialmodelingprep.com/developer/docs/#Stock-Price
#https://financialmodelingprep.com/developer/docs/#Company-Quote
realtime_url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/'
company_info_url = 'https://financialmodelingprep.com/api/v3/quote/'

with open('G:\WEBSCRAP\CompanyList.txt') as CompLists:
    companies = CompLists.readlines()

df = pd.DataFrame(columns = ['symbol', 'name', 'price', 'changesPercentage', 'change', 'dayLow', 'dayHigh', 'yearHigh', 'yearLow', 'marketCap', 'priceAvg50', 'priceAvg200', 'volume' , 'avgVolume', 'exhange', 'open', 'previousClose', 'eps', 'pe', 'earningsAnnouncement', 'sharesOutstanding', 'timestamp'])

for i in range(1,11):
    for counter, company in enumerate(companies[:i*50]):
        company = company.strip()
        url =  company_info_url + company
        price = requests.get(url)
        priceinfo = price.text
        print("({}:{})".format(counter,company))
        datadict = json.loads(priceinfo)
        datadict = datadict[0]
        df = df.append(datadict, ignore_index=True )

    df = df.drop(['earningsAnnouncement', 'timestamp'], axis=1)
    df1 = df[ df['price'] <= df['yearHigh']*.6 ]
    print(df1)
