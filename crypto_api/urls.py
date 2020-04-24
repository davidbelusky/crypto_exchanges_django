from django.urls import path

from .views import ExchangesAllView,ExchangeOneView,DepositsAllView,CryptoCurrenciesAllView,CryptoCurrenciesOneView,TradesAllView,TradeAllHistoryView

urlpatterns = [
    path('exchanges/', ExchangesAllView.as_view(),name='exchanges'),
    path('exchanges/<int:pk>/',ExchangeOneView.as_view(),name='exchange_id'),
    path('deposits/',DepositsAllView.as_view(),name='desposits'),
    path('exchanges/<int:pk>/currencie/',CryptoCurrenciesAllView.as_view(),name='currencies'),
    path('exchanges/<int:pk>/currencie/<int:crypto_pk>/',CryptoCurrenciesOneView.as_view(),name='currencie_id'),
    path('exchanges/<int:pk>/trades/',TradesAllView.as_view(),name='trades'),
    path('trade_history/',TradeAllHistoryView.as_view(),name='trade_history')

]