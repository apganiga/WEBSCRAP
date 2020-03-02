import requests
# import numpy
# import pandas

response = requests.get('https://sg.finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch')
print(response.text)