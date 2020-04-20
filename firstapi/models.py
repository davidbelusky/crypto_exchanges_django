from django.db import models
from .others.corrections import Get_currency_rates
import json
import os


#ONLINE DATA
# fiat,crypto = Get_currency_rates.get_all_assets()
#
# #Currency List ex. [('EUR','Euro),('USD','Dollar')...] Model choices
# currency_list = [(curr['asset_id'],curr['name']) for curr in fiat]
# #Crypto currency list ex. [('BTC','Bitcoin),('ETH','Etherum')....] Model choices
# crypto_name_list = [(curr['asset_id'],curr['name']) for curr in crypto]
# #Dict crypto currency ex. {'BTC':'Bitcoin','ETH':'Etherum'...} (Used in POST crypto currency for automatically filling crypto name based on crypto currency input)
# crypto_name_dict = {curr['asset_id']:curr['name'] for curr in crypto}

#JSON DATA
current_path = os.path.abspath(os.getcwd())
with open(current_path + '\currency_data.txt') as json_file:
    data = json.load(json_file)
currency_list = data['currency_list']
crypto_name_list = data['crypto_name_list']
crypto_name_dict = data['crypto_name_dict']
#Fiat currencies and crypto currencies together. Used for checking currency exist in Trade model
all_currencies = currency_list + crypto_name_list


class Exchanges(models.Model):
    name = models.CharField(max_length=30,unique=True)
    currency = models.CharField(choices=currency_list,max_length=30)
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.name

class Deposits(models.Model):
    exchange_id = models.ForeignKey(Exchanges,on_delete=models.CASCADE)
    currency = models.CharField(choices=currency_list,max_length=30)
    amount = models.FloatField()

    def __str__(self):
        return 'exch ID: {}  curr: {} amt: {}'.format(str(self.exchange_id),self.currency,str(self.amount))

class CryptoCurrencies(models.Model):
    exchange_id = models.ForeignKey(Exchanges,on_delete=models.CASCADE)
    crypto_name = models.CharField(max_length=30,blank=True)
    crypto_currency = models.CharField(choices=crypto_name_list,max_length=30)
    favourite = models.BooleanField(default=False)
    amount = models.FloatField(default=0)

    def __str__(self):
        return 'exch ID: {} crypto_name: {}'.format(str(self.exchange_id),self.crypto_name)

class Trades(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    exchange_id = models.ForeignKey(Exchanges,on_delete=models.CASCADE)
    currency_in = models.CharField(choices=all_currencies,max_length=30)
    currency_out = models.CharField(choices=all_currencies,max_length=30)
    amount = models.FloatField(blank=False)

    def __str__(self):
        return 'exch ID: {} curr_in: {}'.format(str(self.exchange_id),self.currency_in)
