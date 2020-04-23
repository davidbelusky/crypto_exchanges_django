from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

from ..models import Exchanges,CryptoCurrencies,Trades
from ..serializers import TradesSerializer




class TradesGetAllTest(APITestCase):
    def setUp(self):
        self.exchange_1 = Exchanges.objects.create(name='Peter', currency='USD',amount=10000)
        self.crypto_btc = CryptoCurrencies.objects.create(crypto_currency='BTC', exchange_id=self.exchange_1,crypto_name='Bitcoin')
        self.crypto_eth = CryptoCurrencies.objects.create(crypto_currency='ETH', exchange_id=self.exchange_1,crypto_name='Ethereum')

    def test_create_correct_input_trade(self):
        """
        - Test creating trade
        - Test if traded fiat amount was converted and added to crypto currency amount
        - Test if traded fiat amount was converted to exchange currency amount and substracted from exchange amount
        """
        url = reverse('trades', args=(self.exchange_1.id,))
        data = {'currency_in': 'eur', 'currency_out':'btc','amount':2500}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if converted amount was added to specific currency object
        crypto_currency_btc = CryptoCurrencies.objects.get(exchange_id=self.exchange_1,crypto_currency='BTC')
        self.assertNotEqual(crypto_currency_btc.amount,0)
        # Check if traded amount was substracted from exchange amount
        updated_exchange = Exchanges.objects.get(id=self.exchange_1.id)
        self.assertLess(updated_exchange.amount,self.exchange_1.amount)
        #Check if traded currency_in 'EUR' amount 2500 was converted to exchange currency 'USD' amount
        self.assertLess(updated_exchange.amount,7500)

    def test_create_incorrect_input_trade(self):
        """
        - Trade amount must be < Exchange amount
        - Trade to crypto currency which is not created for specific exchange_id
        - Trade fiat to fiat
        - Trade crypto to crypto
        - Trade with number which is < 0
        """
        url = reverse('trades', args=(self.exchange_1.id,))
        data = {'currency_in': 'USD', 'currency_out': 'btc', 'amount': 15000}
        #If trade amount > exchange amount, trade cannot be done. Response HTTP 400
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        #Trade to crypto currency 'XRP' which is not created for exchange_id 1. Response HTTP 400
        data = {'currency_in': 'USD', 'currency_out': 'XRP', 'amount': 5000}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        #Trade fiat to fiat currency. Only fiat to crypto or crypto to fiat is allowed. Response HTTP 400
        data = {'currency_in': 'USD', 'currency_out': 'EUR', 'amount': 5000}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #Trade crypto to crypto currency. Response HTTP 400
        data = {'currency_in': 'BTC', 'currency_out': 'ETH', 'amount': 5000}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #Trade negative amount. Amount must be > 0. Response HTTP 400
        data = {'currency_in': 'usd', 'currency_out': 'btc', 'amount': -5000}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_trades(self):
        """
        Test GET all crypto currencies
        - Test count of created objects (2)
        - Test if GET request show all same objects as in saved in model
        """
        #Create objects for testing get all trades
        Trades.objects.create(exchange_id=self.exchange_1, currency_in='EUR', currency_out='BTC', amount=500)
        Trades.objects.create(exchange_id=self.exchange_1, currency_in='USD', currency_out='ETH', amount=500)

        url = reverse('trades', args=(self.exchange_1.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_data = json.dumps(TradesSerializer(instance=Trades.objects.all(), many=True).data)
        serialized_data = json.loads(serialized_data)
        response_data = json.loads(response.content)
        # Check if get 2 created objects
        self.assertEqual(len(serialized_data), len(response_data))
        # Check if data in model is same as GET response data
        self.assertEqual(serialized_data, response_data)




