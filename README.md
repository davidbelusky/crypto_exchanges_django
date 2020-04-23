# Crypto currency exchange API

## Startup:

1. Enable virtual environment: `virtualenv venv` (You need to have installed **virtualenv** pip module - `pip install virtualenv`)
2. Switch to virtualenv: `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: in project folder open terminal: `py manage.py runserver`
5. To run tests use: `py manage.py test`

## Info:
**Crypto currencies trading** - 
- Create exchange. Fields: id, name, currency (fiat),amount
- Deposit amount to exchange_id. Fields: id, exchange_id (foreign_key), currency, amount
- Crypto currencie for exchange_id. Fields: id, exchange_id (foreign_key), crypto_currency, crypto_name, amount, favourite (boolean)
- Trades for exchange_id. Fields: id, exchange_id (foreign_key), created_date ,currency_in ,currency_out, amount

**Exchange rates** - In model.py are two options default is from json static data 'currency_data.txt'. There is also commented option where is data set to get from online API with actual rates

## Create exchange
### Request:

**_name_** - Name must be unique. Name is automatically capitalize 'david' > 'David'

**_currency_** - Currency in which total amount for exchange will be displayed. Must be 3 letter shortcut of fiat currency ex. 'USD'. Input is automatically converted to uppercase 'usd' > 'USD'

**POST** `/exchanges`
```json 
{
  "name": "first_exchange",
  "currency":"eur" 
}
```

### Response:
New created object or error message. 
```json 
{
  "id":1
  "name": "First_exchange",
  "currency":"EUR",
  "amount":0
}
```

## Deposit exchange
### Request:

**_amount_** - Float number

**_currency_** - 3 letter shortcut of fiat currency. If deposit currency != exchange_id currency convert deposit currency to exchange currency and insert to exchange. ex. 'EUR'     

**POST** `/exchanges/{int:exchange_id}/`
```json
{
  "amount": 50,
  "currency": "USD"
} 
```

### Response:
'Success' or error message


## Update cryptocurrencies within exchange
### Request:

**_name_** - Crypto name ex. 'Bitcoin', mandatory if **currency** is not inserted.

**_currency_** - Crypto currency 3 letter shortcut ex. 'BTC', mandatory if **name** is not inserted.

**_favourite_** - Boolean True/False. Default = False

**PUT** `/exchanges/{int:exchange_id}/currencie`
 ```json
{
  "name": "Bitcoin",
  "Favourite": true
} 
```

**Inputted name/currency or both of them:** 

- **CREATE** If name/currency doesnt exist for exchange_id then create this crypto currency

- **DELETE** If name/currency exist for exchange_id then delete this crypto currency

**Inputted name/currency or both of them and favourite:**

- **CREATE** If name/currency doesnt exist for exchange_id then create it with custom favourite.

- **UPDATE** If name/currency exist for exchange_id then update favourite parameter in DB

### Response:
All crypto currencies for specific exchange_id or error message.

```json 
[
  {
    "amount": 0.13147733829748992,
    "curr": "BTC",
    "exchange_id": 77,
    "favourite": false,
    "id": 20,
    "name": "Bitcoin"
  },
  {
    "amount": 0.48218492007340913,
    "curr": "BTC",
    "exchange_id": 79,
    "favourite": false,
    "id": 21,
    "name": "Bitcoin"
  }
]
```

## Create trade
### Request:

**_amount_** - Float number

**_currency_in_** - 3 letter shortcut fiat/crypto currency

**_currency_out_** - 3 letter shortcut fiat/crypto currency 

**POST** /exchanges/{int:exchange_id}/trades
```json 
{
	"currency_in": "usd",
	"currency_out": "btc",
	"amount":5000
}
```

### Info:
- Cannot convert from fiat to fiat or crypto to crypto. Only fiat to crypto or crypto to fiat is allowed
- Check if trade amount <= balance amount
- Convert trade fiat to exchange fiat currency
- Add/Substract from crypto and exchange based on operation

### Response:
traded amount, actual exchange currency amount,exchange currency or error message

```json 
{
    "actual_amount": 0.9818410621979138,
    "currency": "BTC",
    "exchanged_amount": 0.491053058849187
}
```

## History of trades
### Request:
**_offset_** - start from

**_limit_** - max to show

**_exchange_id_** - unique index

**_search_** - searching contain text in trade table and column 'name'. ex. ('Bitcoin','B','coin')

**_date_from_** - trade_date >= date_from

**_date_to_**  - trade_date <= date_to

**GET** `/history?offset={offset}&limit={limit}&exchange_id={exchange_id}&search={search}&date_from={date_from}&date_to={date_to}`

ex. ```URL http://127.0.0.1:5000/exchanges/history?exchange_id=1&limit=5&offset=2&search=Bi&date_from=5.11.2019&date_to=15.2.2020```

### Response:
list of json records with applied parameters filter

```json  
[
  {
    "amount": 5000.0,
    "curr_in": "USD",
    "curr_out": "BTC",
    "exchange_id": 81,
    "id": 26,
    "name": "Bitcoin",
    "trade_date": "Thu, 13 Feb 2020 18:42:09 GMT"
  },
  {
    "amount": 5.0,
    "curr_in": "USD",
    "curr_out": "BTC",
    "exchange_id": 81,
    "id": 27,
    "name": "Bitcoin",
    "trade_date": "Thu, 13 Feb 2020 18:42:21 GMT"
  },
  {
    "amount": 1.0,
    "curr_in": "USD",
    "curr_out": "BTC",
    "exchange_id": 81,
    "id": 28,
    "name": "Bitcoin",
    "trade_date": "Thu, 13 Feb 2020 18:42:28 GMT"
  }
]
```
