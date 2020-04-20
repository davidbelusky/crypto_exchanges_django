from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

from ..models import Exchanges,CryptoCurrencies
from ..serializers import ExchangesSerializer,CryptoCurrenciesSerializer



class CryptoCurrenciesAllTestCase(APITestCase):
    def setUp(self):
        self.exchange_1 = Exchanges.objects.create(name='Peter', currency='USD')
        self.exchange_2 = Exchanges.objects.create(name='Tomas', currency='EUR')
        CryptoCurrencies.objects.create(crypto_currency='BTC', exchange_id=self.exchange_1, crypto_name='Bitcoin')
        CryptoCurrencies.objects.create(crypto_currency='ETH', exchange_id=self.exchange_1, favourite=True,crypto_name='Ethernet')

    def test_get_crypto_currencies(self):
        """
        Test GET all crypto currencies
        - Test count of created objects (2)
        - Test 'favourite' default input
        """
        #exchange_1 = Exchanges.objects.get(name='Peter')
        url = reverse('currencies', args=(self.exchange_1.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        # Get all objects from DB and serialize them
        serialized_data = json.dumps(CryptoCurrenciesSerializer(instance=CryptoCurrencies.objects.all(), many=True).data)
        serialized_data = json.loads(serialized_data)
        response_data = json.loads(response.content)
        #Check if get 2 created objects
        self.assertEqual(len(serialized_data), len(response_data))
        #Check if data in model is same as GET response data
        self.assertEqual(serialized_data,response_data)

        #First object have default 'favourite' set to False
        self.assertFalse(response_data[0]['favourite'])
        #Second object have optionaly set 'favourite' to True
        self.assertTrue(response_data[1]['favourite'])

    def test_create_crypto_currencie(self):
        """
        - Check status code 201 created
        - Check correct set favourite to default: False
        - Check autofill field 'crypto_name' to Bitcoin based on 'crypto_currency':'BTC'
        - Check amount must be always set to 0 after created new crypto currency
        - Check correct foreign key set to 2 exchange_id
        """
        data = {'crypto_currency':'btc','amount':500}
        #set url to exchange_id 2
        url = reverse('currencies', args=(self.exchange_2.id,))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = json.loads(response.content)[0]
        self.assertFalse(response_data['favourite'])
        self.assertEqual(response_data['crypto_name'],'Bitcoin')
        self.assertEqual(response_data['crypto_currency'], 'BTC')
        #Created crypto currency must have always set amount to 0
        self.assertEqual(response_data['amount'], 0)
        self.assertEqual(response_data['exchange_id'], 2)

    def test_create_crypto_currencie_wrong_input(self):
        """
        - input not existing crypto currency
        - input fiat currency to crypto currency
        - input already existing crypto currency for exchange_id 2
        """

        url = reverse('currencies', args=(self.exchange_1.id,))
        #crypto_currency doesnt exist
        data = {'crypto_currency':'zzz'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        #try to input fiat currency as crypto_currency
        data = {'crypto_currency': 'eur'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #Try to create already existed crypto_currency for exchange_id 1
        data = {'crypto_currency': 'btc'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CryptoCurrenciesOneTestCase(APITestCase):
    def setUp(self):
        self.exchange = Exchanges.objects.create(name='Peter', currency='USD')
        self.crypto = CryptoCurrencies.objects.create(crypto_currency='BTC', exchange_id=self.exchange, crypto_name='Bitcoin')

    def test_get_crypto_currencie(self):
        """
        - Get specific crypto_currencie based on exchange_id and crypto_currency ID
        - Check if URL response correct crypto_currency ID
        """
        url = reverse('currencie_id', args=(self.exchange.id,self.crypto.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        #Check if correct ID was responsed by url
        self.assertEqual(self.crypto.id,response_data['id'])
        self.assertEqual(response_data['crypto_name'],'Bitcoin')

    def test_put_crypto_currencie(self):
        """
        Only field 'favourite' can be changed
        - Change favourite from False to True for crypto currency ID 1
        """
        data = {'favourite':True}
        url = reverse('currencie_id', args=(self.exchange.id, self.crypto.id))
        response = self.client.put(url, data, format='json')
        #Check If put was successfully
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        exchange = CryptoCurrencies.objects.get(id=1)
        #Check if field 'favourite' was changed to True
        self.assertTrue(exchange.favourite)

    def test_delete_crypto(self):
        url = reverse('currencie_id', args=(self.exchange.id, self.crypto.id))
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)




