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
    final_filter = ''
    for k,v in kwargs.items():
        filter_url = '{filter}={value}&'.format(filter=k,value=v)
        final_filter += filter_url

    return final_filter


class TradeHistoryGet(APITestCase):
    def setUp(self):
        self.exchange_1 = Exchanges.objects.create(name='Peter', currency='USD')
        self.exchange_2 = Exchanges.objects.create(name='Denis', currency='USD')
        # self.crypto_btc_1 = CryptoCurrencies.objects.create(crypto_currency='BTC', exchange_id=self.exchange_1,crypto_name='Bitcoin')
        # self.crypto_eth_1 = CryptoCurrencies.objects.create(crypto_currency='ETH', exchange_id=self.exchange_1,crypto_name='Ethereum')
        # self.crypto_btc_2 = CryptoCurrencies.objects.create(crypto_currency='BTC', exchange_id=self.exchange_1,crypto_name='Bitcoin')
        Trades.objects.create(currency_in='USD',currency_out='BTC',amount=500,exchange_id=self.exchange_1)
        Trades.objects.create(currency_in='CZK', currency_out='ETH', amount=12000, exchange_id=self.exchange_1)
        Trades.objects.create(currency_in='USD', currency_out='ETH', amount=250, exchange_id=self.exchange_2)
        Trades.objects.create(currency_in='BTC', currency_out='EUR', amount=1.5, exchange_id=self.exchange_2)
        Trades.objects.create(currency_in='BTC', currency_out='USD', amount=4, exchange_id=self.exchange_2)

    def test_get_history_trades(self):
        url = reverse('trade_history')
        #Generate URL with filter parameters
        filters = filter_generate(exchange_id__id='1', exchange_id__name__iexact='Peter')
        url += '?' + filters

        response = self.client.get(url, format='json')
        print(response.data)
        #self.assertEqual(response.data['count'],5)




