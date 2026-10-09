from django.contrib.auth.models import User
from rest_framework import serializers

from bearings.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    def create(self, validated_data): 
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    class Meta:
        model = Client
        fields = '__all__'
    
class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source='client', 
        queryset=Client.objects.all(),
        write_only=True
    )
    class Meta:
        model = Order
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source='client', 
        queryset=Client.objects.all(),
        write_only=True
    )
    class Meta:
        model = Feedback
        fields = '__all__'

class BearingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bearing
        fields = '__all__'

class OrderCompositionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    bearing = BearingSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        source='order', 
        queryset=Order.objects.all(),
        write_only=True
    )
    bearing_id = serializers.PrimaryKeyRelatedField(
        source='bearing', 
        queryset=Bearing.objects.all(),
        write_only=True
    )
    class Meta:
        model = OrderComposition
        fields = '__all__'
