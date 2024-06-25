"""URL mappings for the user API"""

from django.urls import path
from user import views

app_name = 'user'

# app_name and name="create" are used in test_user_api.py:
# CREATE_USER_URL = reverse('user:create')

urlpatterns = [
    path('/create/', views.CreateUserView.as_view(), name="create"),
    path('/token/', views.CreateTokenView.as_view(), name="token"),
    path('/me/', views.ManageUserView.as_view(), name="me"),
]
