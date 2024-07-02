from django.urls import path
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('', authapp.login, name='login'),
    path('logout/', authapp.user_logout, name='logout'),
]