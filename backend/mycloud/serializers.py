import re

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)

    # валидация
    # email должен соответствовать формату адресов электронной почты — для проверки можно использовать регулярные выражения;
    # ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

    def validate(self, data):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_pattern, data['email']) is None:
            raise ValidationError("Некорректный email")

        return data