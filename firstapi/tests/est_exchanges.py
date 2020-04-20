from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

from ..models import Exchanges,Deposits
from ..serializers import ExchangesSerializer


class ExchangeAllTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('exchanges')
        Exchanges.objects.create(name='Peter',currency='USD')
        Exchanges.objects.create(name='Tomas', currency='EUR')

    def test_get_all_exchanges(self):
        """
        Test GET ExchangeAllView. Show all objects in model Exchange
        Get response from view and compare with data in model Exchange
        - Test if name was inputted correct and capitalized
        - Test if currency was inputted correct uppercased and amount was inputted as 0
        """
        #Get all objects by response
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #Get all objects from DB and serialize them
        serialized_data = json.dumps(ExchangesSerializer(instance=Exchanges.objects.all(),many=True).data)
        serialized_data = json.loads(serialized_data)
        response_data = json.loads(response.content)
        #Check count of objects (2x objects)
        self.assertEqual(len(serialized_data),len(response_data))
        #Check if response data == DB data
        self.assertEqual(serialized_data,response_data)

        # Check names in DB
        names_list = list(Exchanges.objects.all().values_list('name', flat=True))
        names_list.sort()
        self.assertTrue(names_list == ['Peter', 'Tomas'])
        # Check fields
        exchange_object = Exchanges.objects.get(name='Peter')
        self.assertEqual(exchange_object.currency, 'USD')
        self.assertEqual(exchange_object.amount, 0)

    def test_create_exchange(self):
        """
        Test correct input case
        1. Capitalize name
        2. Uppercase currency
        3. Exchange must be always 0 after creating new exchange
        """
        data = {'name':'david','currency':'eur','amount':500}
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        #Capitalize name
        self.assertEqual(Exchanges.objects.get(name='David').name,'David')
        #Uppercase currency
        self.assertEqual(Exchanges.objects.get(name='David').currency,'EUR')
        #Exchange amount after creating must be 0
        self.assertEqual(Exchanges.objects.get(name='David').amount, 0)

    def test_create_exchange_wrong_inputs(self):
        """
        Test wrong input cases during creating exchange
        1. Field 'name' must be unique
        2. Check if inputted currency exist
        3. Check required input fields ('name','currency')
        """
        data = {'name':'peter','currency':'usd'}
        #Try to create exchange with name which is already in DB. (Name must be unique!)
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        #Wrong currency input (currency doesnt exist)
        data = {'name':'patrik','currency':'abc'}
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        #Missing currency key or name key in input
        del data['currency']
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        data['currency'] = 'USD'
        del data['name']
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

class ExchangeOneTestCase(APITestCase):
    def setUp(self):
        Exchanges.objects.create(name='David', currency='USD',amount=300)
        Exchanges.objects.create(name='Patrik', currency='EUR')

    def test_get_exchange(self):
        """
        Get json data for exchange_id = 1 which name is 'David' and check if response is correct
        """
        url = reverse('exchange_id',args=(1,))
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

        response = json.loads(response.content)
        self.assertEqual(response['id'],1)
        self.assertEqual(response['name'], 'David')
        self.assertEqual(response['currency'], 'USD')

    def test_put_exchange(self):
        """
        Change object(name='David',currency='CZK) to (name='Martin','currency':'EUR')
        And check if amount was converted to new changed currency
        """
        data = {'name':'martin','currency':'EUR'}
        exchange = Exchanges.objects.get(name='David')

        url = reverse('exchange_id',args=(exchange.id,))
        response = self.client.put(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        updated_exchange = Exchanges.objects.get(id=exchange.id)
        #After update exchange id 1 from USD to EUR than if converting was correct amounts cant be equal
        self.assertNotEqual(exchange.amount,updated_exchange.amount)

    def test_post_deposit(self):
        """
        Test POST to one exchange add deposit
        Deposit 100 USD for exchange_id = 2 which name is 'Patrik' and currency 'EUR'.
        Check if deposit amount was converted to exchange currency in exchang_id (USD to EUR)
        """
        exchange = Exchanges.objects.get(name='Patrik')
        data = {'currency':'USD','amount':100}
        url = reverse('exchange_id', args=(exchange.id,))
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        updated_exchange = Exchanges.objects.get(id=exchange.id)
        #Input amount 100 USD cannot equal to converted to EUR amount
        self.assertNotEqual(data['amount'],updated_exchange.amount)
        #Only one deposit was inputted
        self.assertEqual(Deposits.objects.all().count(),1)
        deposit = Deposits.objects.get(exchange_id=2)
        #In deposit model must be same currency and amount as input data
        self.assertEqual(deposit.currency,data['currency'])
        self.assertEqual(deposit.amount,data['amount'])









