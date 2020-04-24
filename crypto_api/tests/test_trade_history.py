from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

from ..models import Exchanges,CryptoCurrencies,Trades

def filter_generate(**kwargs):
    """
    Generate filter URL parameters for URL
    key = filter ex.(exchange_id__id,exchange_id__name)
    value = filtered value ex.(2,'David')
    ex. filter_generate(exchange_id__id=2,exchange_id__name='David')
    Return: filter parameters ex. (?exchange_id__id=2&exchange_id__name__iexact=David&)
    """
    #Filters begin with '?'
    final_filter = '?'
    for k,v in kwargs.items():
        filter_url = '{filter}={value}&'.format(filter=k,value=v)
        final_filter += filter_url

    return final_filter


class TradeHistoryGet(APITestCase):
    def setUp(self):
        self.exchange_1 = Exchanges.objects.create(name='Peter', currency='USD')
        self.exchange_2 = Exchanges.objects.create(name='Denis', currency='USD')
        Trades.objects.create(currency_in='USD',currency_out='BTC',amount=500,exchange_id=self.exchange_1)
        Trades.objects.create(currency_in='CZK', currency_out='ETH', amount=12000, exchange_id=self.exchange_1)
        Trades.objects.create(currency_in='USD', currency_out='ETH', amount=250, exchange_id=self.exchange_2)
        Trades.objects.create(currency_in='BTC', currency_out='EUR', amount=1.5, exchange_id=self.exchange_2)
        Trades.objects.create(currency_in='BTC', currency_out='USD', amount=4, exchange_id=self.exchange_2)

    def test_get_all_history_trades(self):
        """
        Tested filters:
        - exchange_id,exchange name (2 trades created for exchange_id 1 and name Peter)
        - currency_in, currency_out
        """
        #Check if all 5 trades was created
        url = reverse('trade_history')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'],5)

    def test_filter_exchange_id_exchange_name(self):
        """
        - Test filter exchange_id and exchange_name
        Applied filters: exchange_id = 1 and exchange_name = 'Peter'
        results = 2 objects
        """
        #Generate URL with filters (exchange_id,exchange_name)
        filters = filter_generate(exchange_id__id='1', exchange_id__name__iexact='Peter')
        url = reverse('trade_history') + filters
        response = self.client.get(url, format='json')
        #Result = 2 objects for exchange_id = 1 and exchange_name = 'Peter'
        self.assertEqual(response.data['count'],2)
        #Get list of extracted exchange_ids after used filter
        id_list = set(x['exchange_id'] for x in response.data['results'])
        self.assertEqual(len(id_list),1)
        #Only exchange_id 1 must show after applied filter
        self.assertEqual(list(id_list)[0],1)

    def test_filter_currency_in(self):
        """
        - Test filter for currency_in
        Applied filter: currency_in = 'BTC'
        results = 2 objects
        """
        #Get all trades with 'currency_in' = 'BTC'
        filters = filter_generate(currency_in__iexact='BTC')
        url = reverse('trade_history') + filters
        response = self.client.get(url, format='json')
        #Two trades have currency_in 'BTC'
        self.assertEqual(response.data['count'],2)
        #GET only BTC currency_in
        currency_in_list = set(x['currency_in'] for x in response.data['results'])
        self.assertEqual(list(currency_in_list)[0],'BTC')

    def test_filter_currency_out(self):
        """
        - Test filter for currency_out
        Applied filter: currency_out = 'EUR'
        results = 1 object
        """
        # Get all trades with 'currency_out' = 'EUR'
        filters = filter_generate(currency_out__iexact='EUR')
        url = reverse('trade_history') + filters
        response = self.client.get(url, format='json')
        # Two trades have currency_in 'BTC'
        self.assertEqual(response.data['count'], 1)
        # GET only BTC currency_in
        currency_out_list = set(x['currency_out'] for x in response.data['results'])
        self.assertEqual(list(currency_out_list)[0], 'EUR')

    def test_all_filters(self):
        """
        - Tested filters (exchange_id,exchange_name,currency_in,currenecy_out)
        Applied filters: exchange_id = 1,exchange_name = Peter, currency_in = CZK,currency_out = ETH
        result = 1 object
        Compare earned objects from get request and model object
        """
        filters = filter_generate(exchange_id__id='1', exchange_id__name__iexact='Peter',currency_in__iexact='CZK',currency_out__iexact='ETH')
        url = reverse('trade_history') + filters
        response = self.client.get(url, format='json')
        #After applied filter return only 1 object
        self.assertEqual(response.data['count'],1)

        result_value_list = [str(v) for k,v in response.data['results'][0].items() if k != 'created_date' and k != 'amount']
        #Get object from model with same applied filters
        trade_object = Trades.objects.filter(exchange_id__id='1', exchange_id__name__iexact='Peter',currency_in__iexact='CZK',currency_out__iexact='ETH').values()[0]
        trade_object_value_list = [str(v) for k,v in trade_object.items() if k != 'created_date' and k != 'amount']
        #Sort result list from view and object result from model
        result_value_list.sort()
        trade_object_value_list.sort()
        #Check if both show same data
        self.assertEqual(result_value_list,trade_object_value_list)











