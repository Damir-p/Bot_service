from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Message.

    Attributes:
        Meta (class): Внутренний класс, содержащий метаданные сериализатора.
    """

    class Meta:
        model = Message
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Attributes:
        Meta (class): Внутренний класс, содержащий метаданные сериализатора.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        """
        Создает нового пользователя на основе проверенных данных.

        Args:
            validated_data (dict): Проверенные данные пользователя.

        Returns:
            User: Новый объект пользователя, сохраненный в базе данных.
        """
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
