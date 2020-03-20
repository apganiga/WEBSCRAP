import requests
import pandas as pd
import json

#https://financialmodelingprep.com/developer/docs/#Stock-Price
#https://financialmodelingprep.com/developer/docs/#Company-Quote
#https://www.morningstar.com/stocks/screener-compare

def giveCompanyList(companies, start, batchSize):
    companyList = [ comp.strip() for comp in companies[start*batchSize:(start*batchSize)+batchSize]]
    return ','.join(companyList)

def extractTickerInfo(companyList):
    realtime_url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/'
    company_info_url = 'https://financialmodelingprep.com/api/v3/quote/'

    url =  company_info_url + companyList
    prices = requests.get(url)
    prices = json.loads(prices.text)
    df = pd.DataFrame(
        columns=['symbol', 'name', 'price', 'changesPercentage', 'change', 'dayLow', 'dayHigh', 'yearHigh', 'yearLow',
                 'marketCap', 'priceAvg50', 'priceAvg200', 'volume', 'avgVolume', 'exhange', 'open', 'previousClose',
                 'eps', 'pe', 'earningsAnnouncement', 'sharesOutstanding', 'timestamp'])

    for price in prices :
        df = df.append(price, ignore_index=True )

    df = df.drop(['earningsAnnouncement', 'timestamp'], axis=1)
    try:
        df = df[ ( df['price'] <= df['yearHigh']*.4 )]
        df = df[(df['priceAvg50'] / df['priceAvg200']).abs().round() == 1]
    except Exception as e:  ##Improve the  error handling
        exceptionTickers.append(companyList.split(','))
        print("===========> Exception while Filtering Shares:", e)

    return df

if __name__ == '__main__' :
    batchSize=10
    main_df = pd.DataFrame(columns = ['symbol', 'name', 'price', 'changesPercentage', 'change', 'dayLow', 'dayHigh', 'yearHigh', 'yearLow', 'marketCap', 'priceAvg50', 'priceAvg200', 'volume' , 'avgVolume', 'exhange', 'open', 'previousClose', 'eps', 'pe', 'earningsAnnouncement', 'sharesOutstanding', 'timestamp'])

    with open('G:\WEBSCRAP\CompanyList.txt') as CompLists:
        companies = list(set(CompLists.readlines()))

    for i in range((30//batchSize)+1):
    # for i in range((len(companies) // batchSize) + 1):
        companyList = giveCompanyList(companies, i ,batchSize)
        print("Extracting data for:", companyList )
        main_df = main_df.append(extractTickerInfo(companyList))


    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    main_df['changesPercentage'] = main_df['changesPercentage'].round(2).astype(str) + '%'
    main_df['price'] = '$' + main_df['price'].round(2).astype(str)
    main_df['marketCap'] = (main_df['marketCap']/1000000000).round().astype(str) + 'B'

    main_df = main_df.sort_values(['changesPercentage', 'marketCap'], ascending=[False, True])
    # print(main_df[['symbol', 'name', 'price', 'changesPercentage','dayHigh', 'yearHigh', 'priceAvg50', 'priceAvg200', 'marketCap']])
    shortListedCompanies = main_df['symbol'].tolist()
    print(shortListedCompanies)

