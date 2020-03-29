import requests
import json
import pandas as pd
billion = 1000000000

# May be List of Dictionary Causing ISSUE??
## TO HANDLE:
#   1. If Any ticker doesnt return  back,list and tell

ApiDict = {
    'StockPrice': {
        'url': 'https://financialmodelingprep.com/api/v3/stock/real-time-price/',  ## only Mandatory
        'size': 10,  # mandatory
        'deepKey': 'companiesPriceList'  ##Optional
    },
    'CompanyQuote': {
        'url': 'https://financialmodelingprep.com/api/v3/quote/',  # mandatory
        'size': 3,  # mandatory
        'requiredInfo': ['symbol', 'changesPercentage', 'change', 'dayHigh', 'yearHigh', 'marketCap', 'priceAvg50', 'priceAvg200'],  # optonal
        'ops': {'changesPercentage': ['astype(str)'], 'marketCap': ['/billion', '+ "B"']}
        # Implement this Generic Functionality   #Optional
    },
    'CompanyRating': {
        'url': 'https://financialmodelingprep.com/api/v3/company/rating/',
        'size': 3,
        'deepKey': 'companiesRating',
        'deepKey2': 'rating',
        'requiredInfo': ['symbol', 'recommendation']
    }
}

def scrapWebGiveListOfDict(need, tickers):  # Returns List of Dict
    if need not in ApiDict :
        raise NameError("{} is Unrecognized Request".format(need))

    noOfTickers = len(tickers.split(','))
    print(ApiDict[need]['url'] + tickers)
    data_extracted = json.loads((requests.get(ApiDict[need]['url'] + tickers).text))
    # print("AFTER JSON LOADING..:")
    # print(data_extracted)
    if len(data_extracted) > 0 and noOfTickers > 1 :
        print("noOfTickers is:", noOfTickers)
        if len(data_extracted) > 0 and 'deepKey' in ApiDict[need] :
            data_extracted = data_extracted[ApiDict[need]['deepKey']] ## If multiple tickers input, the this API returns dict of dict else it returns only List
            if len(data_extracted) > 0 and 'deepKey2' in ApiDict[need] :
               for i in range(len(data_extracted)):
                   symbol = data_extracted[i]['symbol']
                   second_level_dict = data_extracted[i][ApiDict[need]['deepKey2']]
                   print("Symbol & second_level_dict:", symbol , second_level_dict)
                   flat_dict = dict()
                   flat_dict = { 'symbol': symbol}
                   flat_dict.update(second_level_dict)
                   print("Before Flattening:", data_extracted[i])
                   data_extracted[i] = flat_dict
                   print("After Flattening:", data_extracted[i])

            else:
               pass # This API Call returned List of Dict even though there are multiple tickers. Hence dont need to do anything
    else:
        print('data_extracted = [data_extracted]')
        data_extracted = [data_extracted]

    print("BEFORE CONVERTING TO DATA FRAME:", data_extracted)
    data_extracted = pd.DataFrame(data_extracted)

    if data_extracted.empty :
        return data_extracted # At this point if there are no data in dataframe then return that empty DF

    if not data_extracted.empty and 'requiredInfo' in ApiDict[need] :
        print("requiredInfo defined:", ApiDict[need]['requiredInfo'] )
        print(data_extracted)
        # import pdb; pdb.set_trace()
        print(type(ApiDict[need]['requiredInfo']))
        data_extracted = data_extracted[ApiDict[need]['requiredInfo']]

        data_extracted = data_extracted.set_index('symbol').round(2) #Sets Symbol as index and Rounds of any float to  2 digit
    return data_extracted

def webSrapCaller(info, tickersList):
    validInfo = ApiDict.keys()
    if info not in validInfo:


        print("{} is not a valid call. It should be one of {}".format(info, validInfo))
        raise ValueError

    size = ApiDict[info]['size']
    noOfTickers = len(tickersList)
    main_df = pd.DataFrame()
    for i in range((noOfTickers//size)+1):
       start = i * size
       end = (i*size) ## Omit the  +size to go through the last remaining list
       if end >= noOfTickers:
          break
       tickers = ','.join(tickersList[start:(i*size)+size])
       print("From Caller: Calling for", tickers)
       ## Write Logger to Log the execution details during run time
       df = scrapWebGiveListOfDict(info, tickers)
       main_df = main_df.append(df)
    return main_df


def printdf(df):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df)

TickerFile = 'G:\WEBSCRAP\CompanyList1.txt'
with open(TickerFile) as F_Tickers:
    tickersMasterList = list(set([i.strip() for i in F_Tickers.readlines()]))

tickersList = tickersMasterList[:15]

stockPrice_df = webSrapCaller('StockPrice', tickersList)
# printdf(stockPrice_df)

companyQuote_df =webSrapCaller('CompanyQuote', tickersList)
companyQuote_df['changesPercentage'] = companyQuote_df['changesPercentage'].astype(str) + ' %'
companyQuote_df['marketCap'] = (companyQuote_df['marketCap']/1e9).round(2).fillna(0).astype(str) + 'B'
# printdf(companyQuote_df)

recommendation_df = webSrapCaller('CompanyRating', tickersList )
printdf(recommendation_df)

# final_df  = pd.merge(stockPrice_df, companyQuote_df, recommendation_df, on='symbol', how='outer')
final_df = pd.merge(stockPrice_df, companyQuote_df, on = 'symbol', how = 'inner' )
final_df = pd.merge(final_df, recommendation_df , on = 'symbol', how = 'outer')
printdf(final_df)