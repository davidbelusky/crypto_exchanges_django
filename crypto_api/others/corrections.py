import requests
import json
import os


class InputCorrections():
    @staticmethod
    def currency_name_validate(data):
        """
        Capitalize 'name' of exchange ex.('david' to 'David')
        Uppercase 'currency' of exchange  ex.('usd' to 'USD')
        Uppercase 'crypto_currency' of crypto currrency ex.('btc' to 'BTC')
        Uppercase 'currency_in' and 'currency_out' of Trades ex. ('usd' to 'USD')

        :param data: Input from user during creating exchange, crypto currencie or trade.
        :return:
        """
        if 'name' in data:
            data['name'] = data['name'].capitalize()
        if 'currency' in data:
            data['currency'] = data['currency'].upper()
        if 'crypto_currency' in data:
            data['crypto_currency'] = data['crypto_currency'].upper()
        if 'currency_in' and 'currency_out' in data:
            data['currency_in'] = data['currency_in'].upper()
            data['currency_out'] = data['currency_out'].upper()

        return data
    @staticmethod
    def deposit_amount_validate(data):
        """
        Check if deposit amount is higher than 0
        :param data: Input from user 'currency' and 'amount'
        :return: True if amount is > 0, False if amount is < 0
        """
        if 'amount' in data:
            if data['amount'] < 0:
                return False
        return True
    @staticmethod
    def trade_amount_check_fiat(data,exchange):
        """
        If trading from fiat to crypto check if there is enought amount in exchange
        :param data:
        :return: True if trade amount < exchange amount, If not False
        """
        #Convert trade currency_in amount to exchange currency amount
        converted_amount = Convert_currency.convert(data['currency_in'],exchange.currency,data['amount'])
        #If trade amount > exchange amount return False. Trade cannot be made because there is not enought money in exchange
        if converted_amount > exchange.amount:
            return False
        else:
            return converted_amount
    @staticmethod
    def trade_amount_check_crypto(data,crypto_currencie):
        if data['amount'] > crypto_currencie.amount:
            return False
        return True

class Get_currency_rates():
    @staticmethod
    def get_all_assets():
        """
        Get all assets for fiat and crypto currencies.
        Use for choices in models
        :return: fiat currency list, crypto currency list
        """
        url = 'https://rest.coinapi.io/v1/assets'
        headers = {'X-CoinAPI-Key': '4ED760E9-11CC-4B1D-A423-A263D6BF8FDC'}
        response = requests.get(url, headers=headers).json()

        fiat_list = []
        crypto_list = []
        for asset in response:
            if asset['type_is_crypto'] == 0:
                try:
                    fiat_list.append({'asset_id': asset['asset_id'], 'name': asset['name']})
                except KeyError:
                    fiat_list.append({'asset_id': asset['asset_id'], 'name': 'N/A'})
            elif asset['type_is_crypto'] == 1:
                try:
                    crypto_list.append({'asset_id': asset['asset_id'], 'name': asset['name']})
                except KeyError:
                    crypto_list.append({'asset_id': asset['asset_id'], 'name': 'N/A'})

        return fiat_list, crypto_list

    @staticmethod
    def get_crypto_rate(base, quote):
        """
        Currencies can be fiat and crypto
        :param base: currency from
        :param quote: currency to
        :return: dict with informations, time,asset_id_base,asset_id_quote,rate (using only rate)
        """
        # Return rate of crypto currencies
        url = 'https://rest.coinapi.io/v1/exchangerate/{}/{}'.format(base, quote)
        headers = {'X-CoinAPI-Key': '4ED760E9-11CC-4B1D-A423-A263D6BF8FDC'}
        response = requests.get(url, headers=headers)
        json = response.json()
        return json

class Convert_currency():
    """
    convert: If deposit currency != exchange currency then get rate and convert deposit amount to exchange currency amount return (amount * rate)
            If deposit currency == exchange currency then return amount.
    """
    @staticmethod
    def convert(currency_from,currency_to,amount):
        if currency_from != currency_to:
            rate = Get_currency_rates.get_crypto_rate(currency_from, currency_to)['rate']
            return amount * rate
        return amount

class Trade_currency_check():
    """
    Only allowed trades is between fiat and crypto currency. fiat to fiat or crypto to crypto is not allowed
    Check if requested trade is between fiat and crypto currency

    Return True if trade is OK or False if trade is not allowed
    """
    @staticmethod
    def trade_check(currency_in=None,currency_out=None):
        current_path = os.path.abspath(os.getcwd())
        with open(current_path + '\currency_data.txt') as json_file:
            data = json.load(json_file)
        #List of all fiat currencies shortcuts (x[0] = currency shortcut, x[1] = currency name)
        currency_list = [x[0] for x in data['currency_list']]
        #List of all crypto currencies shortcuts
        crypto_name_list = [x[0] for x in data['crypto_name_list']]

        #If currency_in and currency_out are both fiat currency or both of them are crypto currency return False else return True
        if ((currency_in in currency_list) and (currency_out in currency_list)) or ((currency_in in crypto_name_list) and (currency_out in crypto_name_list)):
            return False
        if currency_in in currency_list:
            return {'currency_in':'fiat','currency_out':'crypto'}
        else:
            return {'currency_in':'crypto','currency_out':'fiat'}




