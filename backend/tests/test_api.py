from rest_framework import status
from rest_framework.test import APITestCase

from mycloud.models import User

from rest_framework.authtoken.models import Token

USER_DATA = {
    "username": "Name1LastName1",
    "first_name": "Name1",
    "last_name": "LastName1",
    "email": "email1@ru.ru",
    "password": "1a1b1cD$"
}


class UserTests(APITestCase):

    def test_create_user(self):
        """
        # добавление пользователя
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        response = self.client.post(url, USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['Status'], True)

    def test_create_user_email_exists(self):
        """
        # добавление пользователя с существующим адресом
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        data = {
            "username": "Name2LastName2",
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email1@ru.ru",
            "password": "2a2b2cD$"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['Status'], False)
        self.assertEqual(response.json()['Errors']['email'], ['Пользователь with this email address already exists.'])

    def test_get_userlist(self):
        """
        # вывод списка пользователей
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]['email'], 'email1@ru.ru')

    def test_get_userlis_unauthorized(self):
        """
        # запрос списка пользователей неавторизованным пользователем
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': '123'}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_user_register_confirm(self):
    #     """
    #     # подтверждение почты покупателя
    #     """
    #     url = 'http://127.0.0.1:8000/api/v1/user/register'
    #     self.client.post(url, USER_DATA, format='json')
    #
    #     url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
    #     token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
    #     data = {'email': USER_DATA['email'], 'token': token.key}
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json()['Status'], True)
    #

    def test_login_user(self):
        """
        # логин пользователя
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': USER_DATA['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_logout_user(self):
        """
        # выход пользователя
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/user/logout'
        data = {'username': USER_DATA['username']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_logout_user_unauthorized(self):
        """
        # выход неавторизованного пользователя
        """
        url = 'http://127.0.0.1:8000/api/user/logout'
        data = {'username': '123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['Errors'], 'Пользователь не найден')

    def test_delete_user(self):
        """
        # удаление пользователя
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        user = User.objects.get(username=USER_DATA['username'])
        user.is_superuser = True
        user.is_staff = True
        user.save()
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')

        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        data = {
            "username": "Name2LastName2",
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email2@ru.ru",
            "password": "2a2b2cD$"
        }
        self.client.post(url, data, format='json')

        url = 'http://127.0.0.1:8000/api/user/delete/2/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_delete_user_unauthorized(self):
        """
        # удаление пользователя неавторизованным пользователем
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        data = {
            "username": "Name2LastName2",
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email2@ru.ru",
            "password": "2a2b2cD$"
        }
        self.client.post(url, data, format='json')

        url = 'http://127.0.0.1:8000/api/user/delete/2/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_not_admin(self):
        """
        # удаление пользователя авторизованным пользователем без прав администратора
        """
        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        user = User.objects.get(username=USER_DATA['username'])
        user.is_superuser = False
        user.is_staff = False
        user.save()
        url = 'http://127.0.0.1:8000/api/user/login'
        data = {'username': USER_DATA['username'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')

        url = 'http://127.0.0.1:8000/api/user/register'
        self.client.post(url, USER_DATA, format='json')
        data = {
            "username": "Name2LastName2",
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email2@ru.ru",
            "password": "2a2b2cD$"
        }
        self.client.post(url, data, format='json')

        url = 'http://127.0.0.1:8000/api/user/delete/2/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #
    # def test_get_user_details(self):
    #     """
    #     # детальные данные покупателя
    #     """
    #     url = 'http://127.0.0.1:8000/api/v1/user/register'
    #     self.client.post(url, USER_DATA, format='json')
    #     url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
    #     token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
    #     data = {'email': USER_DATA['email'], 'token': token.key}
    #     self.client.post(url, data, format='json')
    #     url = 'http://127.0.0.1:8000/api/v1/user/login'
    #     data = {'email': USER_DATA['email'], 'password': USER_DATA['password']}
    #     self.client.post(url, data, format='json')
    #     user = User.objects.get(email=USER_DATA['email'])
    #     token = Token.objects.get(user__id=user.id)
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    #     url = 'http://127.0.0.1:8000/api/v1/user/details'
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json()['email'], USER_DATA['email'])


