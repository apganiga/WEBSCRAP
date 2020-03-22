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

def printdf(df,lisToPrint):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df[lisToPrint])

def getCompanyProfile(compList):
    profile_url = 'https://financialmodelingprep.com/api/v3/enterprise-value/'
    profile_url += compList
    print("=====>>>", profile_url, "length:", len(compList.split(',')))
    profile_details =  requests.get(profile_url )
    profile_details = json.loads(profile_details.text)
    if len(compList.split(',')) > 1 :
        profiles = profile_details['enterpriseValuesList']
    else:

        profiles = [profile_details]

    temp_df = pd.DataFrame(columns=['symbol', 'TotalDebt', 'CashCashFlow', 'AsOf', 'EnterpriseVal'])
    temp_df = temp_df[0:0]
    for profile in profiles:
        Symbol = profile['symbol']
        enterpriseValue = profile['enterpriseValues'][0]
        # print("======   ", Symbol, "  ===================")
        # print(type(enterpriseValue))
        # print(enterpriseValue)
        # print("==============================")
        TotalDebt = enterpriseValue["+ Total Debt"]
        CashCashFlow = enterpriseValue['- Cash & Cash Equivalents']
        AsOf = enterpriseValue['date']
        EnterpriseVal= enterpriseValue['Enterprise Value']
        temp_df = temp_df.append({'symbol': Symbol,
                                                  'TotalDebt': TotalDebt,
                                                  'CashCashFlow': CashCashFlow,
                                                  'AsOf': AsOf,
                                                  'EnterpriseVal': EnterpriseVal}, ignore_index=True)
    temp_df['TotalDebt'] = (temp_df['TotalDebt']/1000000000).round(2).astype(str) + 'B'
    temp_df['CashCashFlow'] = (temp_df['CashCashFlow'] / 1000000000).round(2).astype(str) + 'B'
    temp_df['EnterpriseVal'] = (temp_df['EnterpriseVal']/ 1000000000).round(2).astype(str) + 'B'
    # print(temp_df)
    return temp_df

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

    main_df['changesPercentage'] = main_df['changesPercentage'].round(2).astype(str) + '%'
    main_df['price'] = '$' + main_df['price'].round(2).astype(str)
    main_df['marketCap'] = (main_df['marketCap']/1000000000).round(2).astype(str) + 'B'
    main_df = main_df.sort_values(['changesPercentage', 'marketCap'], ascending=[False, True])
    printdf(main_df, ['symbol', 'name', 'price', 'changesPercentage','dayHigh', 'yearHigh', 'priceAvg50', 'priceAvg200', 'marketCap'])

    enterprise_df = pd.DataFrame(columns=['symbol', 'TotalDebt', 'CashCashFlow', 'AsOf', 'EnterpriseVal'])
    shortListedCompanies = main_df['symbol'].tolist()
    # import pdb; pdb.set_trace()
    for i in range((len(shortListedCompanies) //3) +1 ) : #Should use While. as this will go extra round even if the list emptied
        companyList = ""
        companyList = giveCompanyList(shortListedCompanies, i, 3)
        companyList = companyList.strip()
        if len(companyList) == 0 :
            break
        temp_df = getCompanyProfile(companyList)
        enterprise_df = enterprise_df.append(temp_df)
    printdf(enterprise_df, ['symbol', 'TotalDebt', 'CashCashFlow', 'AsOf', 'EnterpriseVal'])
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    main_df = main_df.set_index('symbol').join(enterprise_df.set_index('symbol'))
    # main_df.info(verbose=True)
    # print(main_df.head(3))
    printdf(main_df, ['name', 'price', 'changesPercentage','dayHigh', 'yearHigh', 'priceAvg50', 'priceAvg200', 'marketCap', 'TotalDebt', 'CashCashFlow', 'EnterpriseVal'])
