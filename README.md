# Crypto currency exchange API

## Startup:

1. Enable virtual environment: `virtualenv venv` (You need to have installed **virtualenv** pip module - `pip install virtualenv`)
2. Switch to virtualenv: `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: in project folder open terminal: `py manage.py runserver`
5. To run tests use: `py manage.py test`

## Info:
**Crypto currencies trading** :
- Create exchange: [id, name, currency (fiat), amount]
- Deposit amount to exchange_id: [id, exchange_id (foreign_key), currency, amount]
- Crypto currencie for exchange_id: [id, exchange_id (foreign_key), crypto_currency, crypto_name, amount, favourite (boolean]
- Trades for exchange_id: [id, exchange_id (foreign_key), created_date ,currency_in ,currency_out, amount]


### Sources:
**Exchange rates** - Getting from online API

**Currencie list** - In model.py are two options default is from json static data 'currency_data.txt'. There is also commented option where data getting from online API with actual rates



## Docker setup:

1. Edit django project setting mysite/settings.py 

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'django',
           'USER': 'david',
           'PASSWORD': 'dav',
           'HOST': 'db',
           'PORT': 5432,
       }
   }
   ```

2. Build docker image.
   In django project folder input into terminal

   ```pse
   docker-compose build
   ```

3. Run docker image

   ```pseudocode
   docker-compose up
   ```

## Create exchange
### Request:

**_name_** - Name must be unique. Name is automatically capitalize 'david' > 'David'

**_currency_** - Currency in which total amount for exchange will be displayed. Must be 3 letter shortcut of fiat currency ex. 'USD'. Input is automatically converted to uppercase 'usd' > 'USD'

**GET** `/exchanges`

Show all exchanges

```json 
[
    {
        "id": 1,
        "name": "David",
        "currency": "EUR",
        "amount": 4498.0
    },
    {
        "id": 2,
        "name": "Palo",
        "currency": "CZK",
        "amount": 0.0
    }
]
```

**POST** `/exchanges`
```json 
{
  "name": "david",
  "currency":"eur" 
}
```

#### Response:
New created object or error message. 
```json 
{
  "id":1,
  "name": "David",
  "currency":"EUR",
  "amount":0
}
```
### Get specific exchange by ID
**GET** `/exchanges/{int:exchange_id}/`
Show specific exchange_id 

```json
{
  "id":1,
  "name": "David",
  "currency":"EUR",
  "amount":0
}
```

### Edit specific exchange ID
**PUT** `/exchanges/{int:exchange_id}/`

Allowed fields for editing:

**_name_** - Name can be changed same rules as during POST new exchange

**_currency_** - Currency can be changed. If currency is changed amount automatically convert to new currency for exchange

```json
{
  "name": "Patrik",
  "currency":"USD",
}
```

#### Response:

'Success' or error message. 

## Deposit exchange
### Request:

**_amount_** - Float number

**_currency_** - 3 letter shortcut of fiat currency. If 'deposit' currency not equal to 'exchange_id' currency then convert deposit currency to exchange currency and insert converted amount to exchange.   

**POST** `/exchanges/{int:exchange_id}/`
```json
{
  "amount": 50,
  "currency": "USD"
} 
```

#### Response:
'Success' or error message


## Update cryptocurrencies within exchange
### Request:

**_crypto_currency_** - Crypto currency 3 letter shortcut ex. 'BTC'

**_favourite_** - Boolean True/False. Default = False

**POST** `/exchanges/{int:exchange_id}/currencie`
 ```json
{
  "crypto_currency": "BTC",
  "favourite":true
} 
 ```

#### Response:
Show all crypto currencies for specific exchange_id or error message

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


**PUT** `/exchanges/{int:exchange_id}/currencie/{int:currency_id}`

Only field 'favourite' can be changed (true/false)

 ```json
{
  "crypto_currency": "BTC",
  "favourite": false
} 
 ```

### Response:

Show updated crypto currencie

**DELETE** `/exchanges/{int:exchange_id}/currencie/{int:currency_id}`

#### Response:

HTTP 204 No content

## Create trade
### Request:

**_amount_** - Float number

**_currency_in_** - 3 letter shortcut fiat/crypto currency

**_currency_out_** - 3 letter shortcut fiat/crypto currency 

### Info:
- Cannot convert from fiat to fiat or crypto to crypto. Only fiat to crypto or crypto to fiat is allowed
- Check if trade amount <= exchange amount
- Convert trade fiat currency amount to exchange fiat currency amount
- Add/Substract from crypto and exchange based on operation
- Trades cannot be deleted or edited

**GET** `/exchanges/{int:exchange_id}/trades` 

Show all trades for specific exchange_id

```json 
[
    {
        "id": 1,
        "exchange_id": 1,
        "created_date": "2020-04-20T11:12:54.862624Z",
        "currency_in": "EUR",
        "currency_out": "BTC",
        "amount": 5000.0
    },
    {
        "id": 2,
        "exchange_id": 1,
        "created_date": "2020-04-23T06:53:52.308722Z",
        "currency_in": "BTC",
        "currency_out": "USD",
        "amount": 1.0
    }
]
```

**POST**  `/exchanges/{int:exchange_id}/trades` 
```json 
{
	"currency_in": "eur",
	"currency_out": "eth",
	"amount": 1
}
```

#### Response:

```json 
{
    "id": 1,
    "exchange_id": 1,
    "created_date": "2020-04-23T06:53:52.308722Z",
    "currency_in": "EUR",
    "currency_out": "ETH",
    "amount": 1.0
}
```

## History of trades
### Request:

**_exchange_id_** - unique ID of exchange

**_exchange_name_** - name of exchange (not case-sensitive)

**_currency_in_** - currency_in trade (not case-sensitive)

**_currency_out_** - currency_out trade (not case-sensitive)

**_created_date_** - specific created datetime

**_date_from_** - trade_date >= date_from

**_date_to_**  - trade_date <= date_to

**GET** `/trade_history/`

ex. ```URL http://127.0.0.1:8000/trade_history/?exchange_id__id=1&exchange_id__name__iexact=David&currency_in__iexact=EUR&currency_out__iexact=BTC&created_date=2020-04-20T11%3A12%3A54.862624Z&created_date__lte=&created_date__gte=```

#### Response:
Filtered data

```json  

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "exchange_id": 1,
            "created_date": "2020-04-20T11:12:54.862624Z",
            "currency_in": "EUR",
            "currency_out": "BTC",
            "amount": 5000.0
        },
        {
            "id": 2,
            "exchange_id": 1,
            "created_date": "2020-04-23T06:53:52.308722Z",
            "currency_in": "EUR",
            "currency_out": "ETH",
            "amount": 1.0
        }
    ]
}

```
