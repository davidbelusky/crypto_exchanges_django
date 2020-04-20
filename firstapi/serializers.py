from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Exchanges,currency_list,Deposits,crypto_name_dict,CryptoCurrencies,Trades

class ExchangesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30,validators=[UniqueValidator(queryset=Exchanges.objects.all())])
    currency = serializers.ChoiceField(currency_list)
    amount = serializers.FloatField(read_only=True,default=0)

    def create(self, validated_data):
        return Exchanges.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.currency = validated_data.get('currency',instance.currency)
        #self.context.get parameter context and set 'amount' to new converted amount
        instance.amount = self.context.get("converted_amount")
        instance.save()
        return instance

class DepositsSerializer(serializers.ModelSerializer):
    exchange_id = serializers.PrimaryKeyRelatedField(queryset=Exchanges.objects.all())
    class Meta:
        model = Deposits
        fields = '__all__'

    def create(self, validated_data):
        return Deposits.objects.create(**validated_data)

class CryptoCurrenciesSerializer(serializers.ModelSerializer):
    exchange_id = serializers.PrimaryKeyRelatedField(queryset=Exchanges.objects.all())
    #Set amount for created crypto currency to 0
    amount = serializers.FloatField(default=0,read_only=True,required=False)
    class Meta:
        model = CryptoCurrencies
        fields = '__all__'

    def create(self, validated_data):
        #Add crypto name to input
        validated_data['crypto_name'] = crypto_name_dict[validated_data['crypto_currency']]
        return CryptoCurrencies.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.favourite = validated_data.get('favourite',instance.favourite)
        instance.save()
        return instance

class TradesSerializer(serializers.ModelSerializer):
    exchange_id = serializers.PrimaryKeyRelatedField(queryset=Exchanges.objects.all())
    class Meta:
        model = Trades
        fields = '__all__'

