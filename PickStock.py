import requests
import json
import pandas as pd

ApiDict = {
    'CompanyProfile': {
        'url': 'https://financialmodelingprep.com/api/v3/company/profile/',  ## only Mandatory
        'size': 10,  # mandatory
        'requiredInfo': ['symbol', 'companyName', 'industry', 'sector' ],  # optonal
        'deepKey': 'companyProfiles',  ##Optional
        'deepKey2': 'profile'
    },
    'Financials': {
        'url': 'https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/',  ## only Mandatory
        'size': 3,  # mandatory
        'requiredInfo': ['symbol', 'Total assets', 'Total debt', 'Other Assets', 'Other Liabilities'],  # optonal
        'deepKey': 'financialStatementList',  ##Optional
        'deepKey2': 'financials',
        'deepKey3': 0,
        'ops': {'Total assets': ['"0B" if pd.isnull(x) else str(round(float(x)/1e9, 2))+"B"'], 'Total debt': ['"0B" if pd.isnull(x) else str(round(float(x)/1e9, 2))+"B"'],
                'Other Assets': ['"0B" if x == "" else x' ,'"0B" if pd.isnull(x) else str(round(float(x)/1e9, 2))+"B"'], 'Other Liabilities':['"0B" if x == "" else x' , '"0B" if pd.isnull(x) else str(round(float(x)/1e9, 2))+"B"'] }
    },
    'CompanyQuote': {
        'url': 'https://financialmodelingprep.com/api/v3/quote/',  # mandatory
        'size': 3,  # mandatory
        'requiredInfo': ['symbol', 'price','changesPercentage', 'change', 'dayHigh', 'yearHigh', 'marketCap', 'priceAvg50', 'priceAvg200'],  # optonal
        'ops': {'changesPercentage': ['str(x)+ "%"'], 'marketCap': ['0 if pd.isnull(x) else x', 'str(int(x)//1e9) + "B"']}
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
    try:
        data_extracted = json.loads((requests.get(ApiDict[need]['url'] + tickers).text))
    except Exception as e:
        print("Error: While scrapping:", ApiDict[need]['url'] + tickers)
        print("error=", e)


    if len(data_extracted) == 0 : ## All code below this executes only if data_extracted is not blank
        return
    elif noOfTickers == 1 and isinstance(type(data_extracted), list) :
        data_extracted = [ data_extracted ]
    elif noOfTickers > 1 and 'deepKey' in ApiDict[need] :
        data_extracted = data_extracted[ApiDict[need]['deepKey']] ## If multiple tickers input, the this API returns dict of dict else it returns only List
# To convert to DF, we want is LIST of DICTIONARY, WHere each element of List is a flat dict
## But some API Calls will give dic of dic. Hence below code will flatten it
    # import pdb;pdb.set_trace()
    for i in range(len(data_extracted)):
        symbol = data_extracted[i]['symbol']
        if 'deepKey2' in ApiDict[need] :
           second_level_dict = data_extracted[i][ApiDict[need]['deepKey2']]
           if 'deepKey3' in ApiDict[need]:
                second_level_dict = second_level_dict[ApiDict[need]['deepKey3']]
           flat_dict = dict()
           flat_dict = { 'symbol': symbol}
           flat_dict.update(second_level_dict)
           data_extracted[i] = flat_dict

    data_extracted = pd.DataFrame(data_extracted)
    data_extracted = data_extracted.round(2)
    if data_extracted.empty :
        return data_extracted # At this point if there are no data in dataframe then return that empty DF
    if not data_extracted.empty and 'requiredInfo' in ApiDict[need] :
        data_extracted = data_extracted[ApiDict[need]['requiredInfo']]
        data_extracted = data_extracted.set_index('symbol') #Sets Symbol as index and Rounds of any float to  2 digit
    if 'ops' in ApiDict[need]:
        ops_dict = ApiDict[need]['ops']
        for col in ops_dict.keys() :
            for expr in ops_dict[col] :
                try:
                    data_extracted[[col]] = data_extracted[[col]].applymap(lambda x: eval(expr))
                except Exception as e:
                    print("Error while applying expr: {} on col:{} | error={}".format(expr, col, e))
                    print("URL:", ApiDict[need]['url'] + tickers)
                    printdf(data_extracted[[col]])
                    continue

    return data_extracted

def webScrapCaller(info, tickersList):
    validInfo = ApiDict.keys()
    if info not in validInfo:
        print("{} is not a valid call. It should be one of {}".format(info, validInfo))
        raise ValueError

    size = ApiDict[info]['size']
    noOfTickers = len(tickersList)
    main_df = pd.DataFrame()
    for counter, i in enumerate(range((noOfTickers//size)+1)):
       start = i * size
       end = (i*size) ## Omit the  +size to go through the last remaining list
       if end >= noOfTickers:
          break
       tickers = ','.join(tickersList[start:(i*size)+size])
       ## Write Logger to Log the execution details during run time
       try:
           print("{}: Scrapping {} for {}... ".format(counter, info, tickers))
           df = scrapWebGiveListOfDict(info, tickers)
       except Exception as e:
           print("Error in webSrapCaller: Scrapping {} for >>>{}<<<<...Continuing with next batch ".format(info, tickers))
           print(ApiDict[info]['url'] + tickers, "Error:", e)
           continue
       main_df = main_df.append(df)
    return main_df

def printdf(df, listOfCols=[]):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    if len(listOfCols) > 1:
        print(df[listOfCols])
    else:
        print(df)

TickerFile = 'G:\WEBSCRAP\CompanyList1.txt'
with open(TickerFile) as F_Tickers:
    tickersMasterList = list(set([i.strip() for i in F_Tickers.readlines()]))

tickersMasterList = tickersMasterList[:21]
batchSize=10
for i  in range((len(tickersMasterList)//batchSize)+1) :
    tickersList = tickersMasterList[i*batchSize:(i*batchSize)+batchSize]
    print("Finding some GOOD stocks among {} stocks: {}".format(len(tickersList), ','.join(tickersList)))

    financials_df = webScrapCaller('Financials', tickersList)
    printdf(financials_df)
    quote_df =webScrapCaller('CompanyQuote', tickersList)
    printdf(quote_df)
    recommendation_df = webScrapCaller('CompanyRating', tickersList )
    printdf(recommendation_df)
    # final_df = pd.merge(profile_df, quote_df, on = 'symbol', how = 'inner' )
    # final_df = pd.merge(final_df, recommendation_df , on = 'symbol', how = 'outer', ).fillna('---')
    # final_df = pd.merge(final_df,financials_df, on = 'symbol', how = 'outer')
    #
    # final_df = final_df.sort_values(['sector','recommendation', 'marketCap', 'Total assets', 'Net Debt'], ascending=False)
    # if i == 0 :
    #     headerOffOn = True
    # else:
    #     headerOffOn = False
    #
    # final_df.to_excel('G:\WEBSCRAP\March30_2020.xls', header = headerOffOn, startrow=(i * batchSize) )
    # printdf(final_df, ['sector', 'industry', 'companyName', 'price', 'changesPercentage', 'dayHigh', 'yearHigh', 'marketCap', 'recommendation', 'Total assets', 'Net Debt', 'Other Assets', 'Other Liabilities'])