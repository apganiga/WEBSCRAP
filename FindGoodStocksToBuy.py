import requests
import pandas as pd
import json

#https://financialmodelingprep.com/developer/docs/#Stock-Price
#https://financialmodelingprep.com/developer/docs/#Company-Quote
#https://www.morningstar.com/stocks/screener-compare

realtime_url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/'
company_info_url = 'https://financialmodelingprep.com/api/v3/quote/'

def giveCompanyList(companies, start, batchSize):
    companyList = [ comp.strip() for comp in companies[start*batchSize:(start*batchSize)+batchSize]]
    return ','.join(companyList)

def extractTickerInfo():
    pass
##implement the extraction here  and return the  data Frame
## Once all 51 batch done, then take the rejected tickers and call one by one

with open('G:\WEBSCRAP\CompanyList.txt') as CompLists:
    companies = list(set(CompLists.readlines()))

df = pd.DataFrame(columns = ['symbol', 'name', 'price', 'changesPercentage', 'change', 'dayLow', 'dayHigh', 'yearHigh', 'yearLow', 'marketCap', 'priceAvg50', 'priceAvg200', 'volume' , 'avgVolume', 'exhange', 'open', 'previousClose', 'eps', 'pe', 'earningsAnnouncement', 'sharesOutstanding', 'timestamp'])
main_df = df.copy()
exceptionTickers = list()

for i in range(51):
    companyList = giveCompanyList(companies, i ,10)
    print("Extracting data for:", companyList )
    url =  company_info_url + companyList
    prices = requests.get(url)
    prices = json.loads(prices.text)
    df = df[0:0]
    for price in prices :
        df = df.append(price, ignore_index=True )
        df = df.drop(['earningsAnnouncement', 'timestamp'], axis=1)
    try:
        df = df[ ( df['price'] <= df['yearHigh']*.4 )]
        # df = df[ ( df['price']< 50 ) & ( (df['priceAvg50']/df['priceAvg200']).abs().round() == 1 ) ]
        df = df[(df['priceAvg50'] / df['priceAvg200']).abs().round() == 1]
        main_df = main_df.append(df)
    except Exception as e:  ##Improve the  error handling
        exceptionTickers.append(companyList.split(','))
        print("===========> Exception while Filtering Shares:", e)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

main_df = main_df.drop_duplicates() ##  Bad Code
main_df = main_df.sort_values(['changesPercentage', 'marketCap'], ascending=[False, True])
main_df['marketCap'] = (main_df['marketCap']/1000000000).round().astype(str) + 'B'
print(main_df[['symbol', 'name', 'price', 'changesPercentage','dayHigh', 'yearHigh', 'priceAvg50', 'priceAvg200', 'marketCap']])