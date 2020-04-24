from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .filters import TradeHistoryFilter
from .others.corrections import InputCorrections,Convert_currency,Trade_currency_check
from .models import Exchanges,Deposits,CryptoCurrencies,Trades
from .serializers import ExchangesSerializer,DepositsSerializer,CryptoCurrenciesSerializer,TradesSerializer

class ExchangesAllView(APIView):
    """
    GET: Show all exchanges
    POST: Create new exchange. Required fields:
        - 'name' name is automatically capitalize ex.('David'),
        - 'currency' currency is automatically uppercase ex.('USD','EUR).
    """

    def get(self,request):
        exchanges = Exchanges.objects.all()
        serializer = ExchangesSerializer(exchanges,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        #CAPITALIZE 'name' and UPPERCASE 'currency'
        data = InputCorrections.currency_name_validate(request.data)
        serializer = ExchangesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ExchangeOneView(APIView):
    """
    GET: Show specific exchange based on exchange_id
    POST: Add deposit for exchange_id.
        Required fields:
        -'currency' ex.(USD,eur)
        -'amount' float ex.(10.5, 12)
        Convert deposit amount to exchange currency and add this amount to specific exchange_id. And save deposit to deposits table.

    PUT: Only "name" and "currency" can be changed for specific exchange_id.
    If currency was changed then automatically convert amount to a new currency
    DELETE: Delete specific exchange_id

    """

    def get_object(self,pk):
        try:
            return Exchanges.objects.get(pk=pk)
        except Exchanges.DoesNotExist:
            raise Http404

    def get(self,request,pk):

        exchange = self.get_object(pk)
        serializer = ExchangesSerializer(exchange)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,pk):
        data = InputCorrections.currency_name_validate(request.data)
        data['exchange_id'] = pk
        #If inputted amount is lower than 0 return HTTP 400
        if InputCorrections.deposit_amount_validate(data) == False:
            return Response({'wrong amount':'amount must be > 0'},status=status.HTTP_400_BAD_REQUEST)

        serializer = DepositsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            #Get Exchange object
            exchange = Exchanges.objects.get(pk=pk)
            #Input currency and amount
            currency_from,amount = data['currency'],data['amount']
            #Convert deposit currency amount to exchange currency
            converted_amount = Convert_currency().convert(currency_from,exchange.currency,amount)
            #Append converted amount to exchange total amount
            exchange.amount = exchange.amount + converted_amount
            exchange.save()

            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk):
        #Name and currency can be changed
        exchange = self.get_object(pk)
        #CAPITALIZE 'name' and UPPERCASE currency
        data = InputCorrections.currency_name_validate(request.data)
        #If changing currency convert amount to new currency.
        converted_amount = Convert_currency.convert(exchange.currency,data['currency'],exchange.amount)
        #context - send converted amount to serializer and change old amount to new converted
        serializer = ExchangesSerializer(exchange,data=data,context = {'converted_amount':converted_amount})
        if serializer.is_valid():
            serializer.amount = converted_amount
            serializer.save()
            return Response({'status':'success'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        exchange = self.get_object(pk)
        exchange.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DepositsAllView(APIView):
    """
    GET: Show all deposits
    """
    def get(self,request):
        deposits = Deposits.objects.all()
        serializer = DepositsSerializer(deposits,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class DepositOneView(APIView):
    """
    GET: show specific deposit based on deposit PK
    """

    def get_object(self,pk):
        try:
            return Deposits.objects.get(pk=pk)
        except Deposits.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        deposit = self.get_object(pk)
        serializer = DepositsSerializer(deposit)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CryptoCurrenciesAllView(APIView):
    """
    GET: Show all crypto currencies for specific exchange_id
    POST: required field:
        - 'crypto_currency' (ex.'BTC','eth'),
        optional field:
        - 'favourite' boolean field default = false
    """
    def get_exchange_object(self,pk):
        try:
            return Exchanges.objects.get(pk=pk)
        except Exchanges.DoesNotExist:
            raise Http404

    def get(self,request,pk,creating=None):
        """
        param creating: After created new crypto currencie POST method call GET function and send parameter creating=True
        creating = True: return all crypto currencies and HTTP status 201
        creating = False: return all crypto currencies and HTTP status 200
        """
        #Check if exchange id exist
        self.get_exchange_object(pk)
        currencies = CryptoCurrencies.objects.filter(exchange_id__exact=pk)
        serializer = CryptoCurrenciesSerializer(currencies,many=True)
        #If this function called from posting during creating new crypto currencie return HTTP status 201
        if creating:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,pk):
        data = InputCorrections.currency_name_validate(request.data)
        data['exchange_id'] = pk
        #Check if crypto currency already exist for this exchange_id
        if 'crypto_currency' in data:
            crypto_name_list = CryptoCurrencies.objects.filter(exchange_id__exact=pk).values('crypto_currency')
            #Create list of crypto currencies for specific exchange id
            crypto_name_list = [x['crypto_currency'] for x in crypto_name_list if x['crypto_currency'] != '']
            if data['crypto_currency'] in crypto_name_list:
                return Response({'wrong input':'crypto currency must be unique for exchange ID'},status=status.HTTP_400_BAD_REQUEST)

        serializer = CryptoCurrenciesSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            #Return all crypto currencies for exchange id
            return self.get(request,pk=pk,creating=True)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CryptoCurrenciesOneView(APIView):
    """
    pk = exchange_id
    GET: Get specific crypto currencie based on exchange_id and crypto_currency PK
    PUT: 'favourite' = True or False other fields cannot be changed
    DELETE: Delete crypto_currency based on exchange_id PK and crypto_currency PK
    """
    def get_object(self,pk,crypto_pk):
        try:
            return CryptoCurrencies.objects.get(pk=crypto_pk,exchange_id=pk)
        except CryptoCurrencies.DoesNotExist:
            raise Http404

    def get(self,request,pk,crypto_pk):
        crypto_currencie = self.get_object(pk,crypto_pk)

        serializer = CryptoCurrenciesSerializer(crypto_currencie)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,pk,crypto_pk):
        crypto_currencie = self.get_object(pk,crypto_pk)
        data = request.data
        data['crypto_currency'] = crypto_currencie.crypto_currency
        data['exchange_id'] = pk
        #Uppercase crypto_currency input
        serializer = CryptoCurrenciesSerializer(crypto_currencie,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,crypto_pk):
        crypto_currencie = self.get_object(pk,crypto_pk)
        crypto_currencie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TradesAllView(APIView):
    """
    GET: Get all trades for specific exchange id
    POST: Only fiat to crypto or crypto to fiat can be traded.
    Required fields:
        - 'currency_in' (fiat or crypto)
        - 'currency_out' (fiat or crypto)
        - 'amount' - amount of currency_in (float)

    """
    def get(self,request,pk):
        # Check if exchange id exist
        CryptoCurrenciesAllView().get_exchange_object(pk)
        trades = Trades.objects.filter(exchange_id__exact=pk)
        serializer = TradesSerializer(trades,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,pk):
        exchange = CryptoCurrenciesAllView().get_exchange_object(pk)
        #correct currencies input to uppercase ex. ('usd' to 'USD')
        data = InputCorrections.currency_name_validate(request.data)
        #Add exchange_id from url to input data
        data['exchange_id'] = pk
        #Check if trade amount > 0
        if not InputCorrections.deposit_amount_validate(data):
            return Response({'wrong amount':'amount must be > 0'},status=status.HTTP_400_BAD_REQUEST)
        #Check if trade is between crypto and fiat currency. Fiat and fiat or crypto and crypto cannot be traded.
        #If trade_currency_info = False trade cannot be done. Else return json ex.({'currency_in':'fiat','currency_out':'crypto'})
        trade_currency_info = Trade_currency_check.trade_check(data['currency_in'],data['currency_out'])
        if not trade_currency_info:
            return Response({'wrong currencies':'Trade can be done only with fiat vs crypto or crypto vs fiat'},status=status.HTTP_400_BAD_REQUEST)

        serializer = TradesSerializer(data=data)
        if serializer.is_valid():
            #If trade from fiat to crypto
            if trade_currency_info['currency_in'] == 'fiat':
                # Check if exchange.amount > trade.amount
                converted_amount = InputCorrections.trade_amount_check_fiat(data,exchange)
                #IF converted_amount == False then exchange amount < trade amount. Means that trade cannot be done!
                if not converted_amount:
                    return Response({'status':'exchange amount < trade amount'},status=status.HTTP_400_BAD_REQUEST)
                #Substract trade amount from exchange amount
                exchange.amount = exchange.amount - converted_amount
                exchange.save()
                #Add trade amount to Crypto currencie
                try:
                    crypto_currencie = CryptoCurrencies.objects.get(exchange_id=pk,crypto_currency=data['currency_out'])
                except CryptoCurrencies.DoesNotExist:
                    return Response({'Wrong input currency_out':'crypto currencie {} doesnt exist'.format(str(data['currency_out']))},status=status.HTTP_400_BAD_REQUEST)
                #Convert inputted fiat currency in amount to currency out crypto amount
                converted_crypto_amount = Convert_currency.convert(data['currency_in'],data['currency_out'],data['amount'])
                crypto_currencie.amount = crypto_currencie.amount + converted_crypto_amount
                crypto_currencie.save()
            #If trade from crypto to fiat
            elif trade_currency_info['currency_in'] == 'crypto':
                #Check if crypto currencie exist
                try:
                    crypto_currencie = CryptoCurrencies.objects.get(exchange_id=pk,crypto_currency=data['currency_in'])
                except CryptoCurrencies.DoesNotExist:
                    return Response({'Wrong input currency_out': 'crypto currencie {} doesnt exist'.format(str(data['currency_in']))}, status=status.HTTP_404_NOT_FOUND)
                #Check if input amount > crypto amount so there is enought amount to finish trade
                if not InputCorrections.trade_amount_check_crypto(data,crypto_currencie):
                    return Response({'Wrong amount input':'input amount > crypto amount'},status=status.HTTP_400_BAD_REQUEST)
                #Substract crypto amount from crypto currencie
                crypto_currencie.amount = crypto_currencie.amount - data['amount']
                crypto_currencie.save()
                #Convert inputted crypto amount to fiat currencie
                converted_amount = Convert_currency.convert(data['currency_in'],data['currency_out'],data['amount'])
                exchange.amount = exchange.amount + converted_amount
                exchange.save()

            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        #converted_amount = Convert_currency().convert(currency_from, exchange.currency, amount)

class TradeAllHistoryView(generics.ListAPIView):
    """
    PAGE PAGINATION = 10

    exchange_id ID = ID of exchange (integer)
    exchange_id name = name of exchange (case-insensitive)
    currency_in = currency_in (case-insensitive)
    currency_out = currency_out (case-insensitive)
    created_date = specific datetime created of trade or from created date to created date
    """

    queryset = Trades.objects.all()
    serializer_class = TradesSerializer
    filterset_class = TradeHistoryFilter




