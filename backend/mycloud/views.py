from django.contrib.auth import authenticate, login, logout
from rest_framework import permissions, status
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q, Sum, F
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from yaml import load as load_yaml, Loader
from distutils.util import strtobool
#from ujson import loads as load_json
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import User
from .serializers import UserSerializer

#TODO
# (+)регистрация пользователя — с валидацией входных данных на соответствие требованиям, описанным выше;
# (+)получение списка пользователей;
# удаление пользователя;
# (+)аутентификация пользователя;
# (+)выход пользователя из системы — logout.
#
# валидация
# (+)логин — только латинские буквы и цифры, первый символ — буква, длина от 4 до 20 символов;
# (+)email должен соответствовать формату адресов электронной почты — для проверки можно использовать регулярные выражения;
# (+)пароль — не менее 6 символов: как минимум одна заглавная буква, одна цифра и один специальный символ.

class RegisterAccount(APIView):
    @extend_schema(
        summary="Регистрация пользователя",
        description="Создаёт нового пользователя с уникальным email, именем и фамилией. "
                    "логин — только латинские буквы и цифры, первый символ — буква, длина от 4 до 20 символов "
                    "email должен соответствовать формату адресов электронной почты "
                    "пароль — не менее 6 символов: как минимум одна заглавная буква, одна цифра и один специальный символ.",
        request=UserSerializer,
        responses={
            201: OpenApiResponse(response=UserSerializer, description="Пользователь успешно создан"),
            400: OpenApiResponse(description="Ошибки валидации")
        }
    )
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'username', 'first_name', 'last_name', 'email', 'password', }.issubset(request.data):
            errors = {}

            # проверяем пароль на сложность

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.is_active = True
                    user.save()
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True}, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

class UserList(APIView):
    @extend_schema(
        summary="Получение информации обо всех пользователях",
        description="Возвращает список всех зарегистрированных пользователей.",
        responses={
            200: OpenApiResponse(response=UserSerializer(many=True), description="Список всех пользователей"),
            403: OpenApiResponse(description="Log in required")
        }
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Errors': 'Log in required'}, status=status.HTTP_403_FORBIDDEN)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDelete(APIView):
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    @extend_schema(
        summary="Удаление пользователя",
        description="Удаляет пользователя по его ID. Если пользователь не найден, возвращает ошибку.",
        responses={
            200: OpenApiResponse(description="Пользователь успешно удалён"),
            400: OpenApiResponse(description="ID пользователя не предоставлен"),
            403: OpenApiResponse(description="Log in required"),
            404: OpenApiResponse(description="Пользователь не найден")
        }
    )
    def delete(self, request, user_id):

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                user.delete()
                return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'Status': False, "Errors": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({'Status': False, "Errors": "ID пользователя не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)


# class ConfirmAccount(APIView):
#     """
#     Класс для подтверждения почтового адреса
#     """
#
#     # Регистрация методом POST
#     def post(self, request, *args, **kwargs):
#
#         # проверяем обязательные аргументы
#         if {'email', 'token'}.issubset(request.data):
#
#             token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
#                                                      key=request.data['token']).first()
#             if token:
#                 token.user.is_active = True
#                 token.user.save()
#                 token.delete()
#                 return JsonResponse({'Status': True})
#             else:
#                 return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})
#
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


# class AccountDetails(APIView):
#     """
#     Класс для работы данными пользователя
#     """
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]
#
#     # получить данные
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)
#
#     # Редактирование методом POST
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#         # проверяем обязательные аргументы
#
#         if 'password' in request.data:
#             errors = {}
#             # проверяем пароль на сложность
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 error_array = []
#                 # noinspection PyTypeChecker
#                 for item in password_error:
#                     error_array.append(item)
#                 return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
#             else:
#                 request.user.set_password(request.data['password'])
#
#         # проверяем остальные данные
#         user_serializer = UserSerializer(request.user, data=request.data, partial=True)
#         if user_serializer.is_valid():
#             user_serializer.save()
#             return JsonResponse({'Status': True})
#         else:
#             return JsonResponse({'Status': False, 'Errors': user_serializer.errors})
#

class LoginAccount(APIView):
    @extend_schema(
        summary="Логин пользователя в систему",
        description="Возвращает токен при успешном логине.",
        responses={
            200: OpenApiResponse(description="Успешный вход в систему"),
            400: OpenApiResponse(description="Не указаны все необходимые аргументы"),
            401: OpenApiResponse(description="Не удалось авторизовать")
        }
    )
    def post(self, request, *args, **kwargs):

        if {'username', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is not None:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)

                return JsonResponse({'Status': True, 'Token': token.key}, status=status.HTTP_200_OK)

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'}, status=status.HTTP_401_UNAUTHORIZED)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAccount(APIView):
    @extend_schema(
        summary="Выход пользователя из системы",
        description="Производит выход пользователя из системы и удаляет токен.",
        responses={
            200: OpenApiResponse(description="Успешный выход из системы"),
            400: OpenApiResponse(description="Не указаны все необходимые аргументы"),
            404: OpenApiResponse(description="Пользователь не найден")
        }
    )
    def post(self, request, *args, **kwargs):

        if {'username'}.issubset(request.data):
            try:
                logout(request)
                user = User.objects.get(username=request.data['username'])
                token, _ = Token.objects.get_or_create(user=user)
                token.delete()

                return JsonResponse({'Status': True}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'Status': False, 'Errors': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'Status': False, 'Errors': 'Произошла ошибка при выходе из аккаунта', 'error': str(e)},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)
