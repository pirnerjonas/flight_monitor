'''
since i am leveraging the monthly calender function of the sas site, the
behaviour of the fields outDate and inDate is a little bit weird.
The api always returns values for one whole month. So if you call the api on
15.09 it returns values till mid october as well.
For future month (>10 in this example) it is easy to extract the whole
months with the api (out and inDate do not matter exactly as long as in is
in the disired month)
'''
import os
import json
import requests
import pandas as pd

from random import choice
from datetime import datetime
from dateutil.relativedelta import relativedelta

DATA_DIR = 'data/'

# set up data folder
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# open settings file
with open("settings.json") as json_data_file:
    settings = json.load(json_data_file)

desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
def random_headers():
    return {'User-Agent': choice(desktop_agents)}

def get_flight_prices(from_airport, to_airport, num_months):
    ''' extract monthly flight prices from the low price calender of the
        SAS website
    '''
    flight_df = pd.DataFrame()
    init_date = datetime.now().date()

    # get prices per month
    for i in range(0, num_months+1):
        next_date = init_date + relativedelta(months=i)
        string_date = next_date.strftime('%Y%m%d')

        # create flysas api request
        url = 'https://api.flysas.com/offers/flights?displayType=CALENDAR&' + \
              'channel=web&bookingFlow=REVENUE&adt=1&' + \
              'outDate={}&inDate={}&'.format(string_date, string_date) + \
              'from={}&to={}&pos=lu'.format(from_airport, to_airport)

        response = requests.get(url, headers=random_headers())

        # if everything goes well
        if response.status_code == 200:
            # get data
            monthly_prices = response.json()
            # extract the relevant info of the raw request data
            monthly_prices = [(datetime.strptime(date, '%Y-%m-%d').date(),
                              price['totalPrice'])
                              for (date, price)
                              in monthly_prices['outboundLowestFares'].items()]
            # remove observations which are not in the current month
            if next_date == init_date:
                monthly_prices = [(date, price) for (date, price) in monthly_prices
                                  if date.month == init_date.month
                                  and date.year == init_date.year]
            # append monthly data
            flight_df = flight_df.append([
                            pd.DataFrame(monthly_prices, columns=['flight_date',
                                                                  'price'])
                        ])
        # other response code
        else:
            return response

    # insert general info
    flight_df['crawl_date'] = init_date.strftime('%Y-%m-%d')
    flight_df['from_airport'] = from_airport
    flight_df['to_airport'] = to_airport

    return flight_df


def main():

    # for every item in the settings write a file
    for from_airport, to_airport, num_months in zip(settings['from_airport'],
                                                    settings['to_airport'],
                                                    settings['num_months']):

        # store some information about the file in the name
        file_name = '{}-'.format(from_airport) + \
                    '{}-'.format(to_airport) + \
                    '{}'.format(datetime.now().date().strftime('%Y%m%d')) + \
                    '.csv'

        # call method
        flight_return = get_flight_prices(from_airport, to_airport, num_months)

        if isinstance(flight_return, pd.DataFrame):
            flight_return.to_csv(DATA_DIR + file_name, index=False)
            print('successfully wrote file {}'.format(file_name))
        else:
            print(f'status code {flight_return.status_code}')

if __name__ == "__main__":
    main()
