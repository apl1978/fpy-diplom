from django.urls import path
from rest_framework.routers import DefaultRouter
# from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from .views import RegisterAccount, UserList, LoginAccount, LogoutAccount, UserDelete
    # ShopViewSet, CategoryViewSet, PartnerUpdate, , ConfirmAccount, AccountDetails, \
    # , ContactView, ProductInfoView, PartnerState, PartnerOrders, BasketView, OrderView

router = DefaultRouter()
# router.register('shops', ShopViewSet, basename='shops')
# router.register('categories', CategoryViewSet, basename='categories')
# router.register('products', ProductInfoView, basename='products')

app_name = 'mycloud'
urlpatterns = [
                  path('user/register', RegisterAccount.as_view(), name='user-register'),
                  path('user/delete/<int:user_id>/', UserDelete.as_view(), name='user-delete'),
                  path('users/', UserList.as_view(), name='user-list'),
                  # path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
                  # path('user/details', AccountDetails.as_view(), name='user-details'),
                  path('user/login', LoginAccount.as_view(), name='user-login'),
                  path('user/logout', LogoutAccount.as_view(), name='user-logout'),
                  # path('user/contact', ContactView.as_view(), name='user-contact'),
                  # path('user/password_reset', reset_password_request_token, name='password-reset'),
                  # path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),

              ] + router.urls
