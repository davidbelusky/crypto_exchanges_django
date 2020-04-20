from django_filters import rest_framework as filters
from .models import Trades


class TradeHistoryFilter(filters.FilterSet):
    class Meta:
        model = Trades
        fields = {
            'exchange_id__id':['exact'],
            'exchange_id__name':['iexact'],
            'currency_in':['iexact'],
            'currency_out':['iexact'],
            'created_date':['exact','lte','gte']

        }
