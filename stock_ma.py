__author__ = 'alex parij'

import argparse
import csv
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs4



def scrape_data(symbol, lookback_period):
    MAX_PER_PAGE = 66

    close_data = []
    start_from = 0
    while start_from < lookback_period:
        url = 'http://finance.yahoo.com/q/hp?s=%s&d=2&e=24&f=2014&g=d&a=2&b=13&c=1986&z=66&y=%s' % (symbol, start_from)
        r = requests.get(url)
        soup = bs4(r.content)
        row_count = 0
        for row in soup.findAll('td',attrs={'class':'yfnc_tabledata1'}):
            if row_count == 6:
                close_data.append(float(row.contents[0].replace(',','')))
                row_count=0
            else:
                row_count += 1
        start_from += MAX_PER_PAGE
    print close_data
    print len(close_data)
    return close_data



def download_data(symbol):
    '''
        Just download the whole set without the lookback cutoff , too complicated to impliment 
        dates because of holidays and weekends

    '''
    prices_url = 'http://ichart.finance.yahoo.com/table.csv?s=%s&d=2&e=24&f=2014&g=d&a=2&b=13&c=1986&ignore=.csv' % symbol
    r = requests.get(prices_url)
    csv_str= r.content
    return csv_str


def process(csv_str):
    '''
        csv has these Columns
        Date	| Open	|  High	|  Low	|  Close  |	Volume	|  Adj Close

        returns Adjusted Close data
    '''
    data = []
    reader = csv.reader(csv_str.split('\n'), delimiter=',')
    reader.next()

    for row in reader:
        if len(row)==7:
            data.append(float(row[6]))

    return data

def calculate_ma(close_data, ma_window, lookback_period):
    '''


    '''
    if ma_window <= 0 or lookback_period < ma_window:
        return []
        
    ma = []
    
    period_data = close_data[-lookback_period:]
    i=0
    while i < (lookback_period-ma_window+1) :
        ma.append(sum(period_data[i:i+ma_window])/ma_window)
        i += 1        
    return ma    

def display_results(close_data, ma_result, lookback, window, symbol):
    plt.figure()
    plt.plot(range(window,len(ma_result)+window), ma_result, 'b-' , label="Moving Average of %s with %s days window" % (symbol,window))
    plt.plot(range(0,lookback), close_data[-lookback:], 'r-', label = "Original Series of %s" % symbol)
    plt.legend()
    plt.show()

    
if __name__ == '__main__':
    '''
        Example arguments to run the script --method scrape --symbol GOOG --lookback 100 --window 10
            
    '''
    parser = argparse.ArgumentParser(description='Calculate MA')
    parser.add_argument('--method', required=False, default= "csv", choices=['scrape','csv'], help='scrape or download csv')
    parser.add_argument('--symbol', required=False, default= "MSFT", help='Stock Symbol')
    parser.add_argument('--lookback', required=False, type=int, default=100,
                        help='Lookback period default 100')
    parser.add_argument('--window', required=False, type=int, default=10,
                        help='Moving average window default 10')
    args = parser.parse_args()

    if args.method =='scrape':
        close_data = scrape_data(args.symbol, args.lookback)
    else:
        csv_str = download_data(args.symbol )
        close_data = process(csv_str)
    print close_data
    close_data.reverse()
    ma_result = calculate_ma(close_data, args.window, args.lookback)
    display_results(close_data, ma_result, args.lookback, args.window, args.symbol)

