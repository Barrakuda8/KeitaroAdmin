from django.urls import path
import adminapp.views as adminapp

app_name = 'adminapp'

urlpatterns = [
    path('stats/', adminapp.stats, name='stats'),
    path('filter_by_date/', adminapp.filter_by_date, name='filter_by_date'),
    path('change_password/', adminapp.change_password, name='change_password'),
    path('users/create/', adminapp.UserCreateView.as_view(), name='create_user'),
    path('users/edit/<int:pk>/', adminapp.UserEditView.as_view(), name='edit_user'),
    path('users/delete/<int:pk>/', adminapp.UserDeleteView.as_view(), name='delete_user'),
    path('supports/create/', adminapp.SupportCreateView.as_view(), name='create_support'),
    path('supports/edit/<int:pk>/', adminapp.SupportEditView.as_view(), name='edit_support'),
    path('accounts/', adminapp.AccountListView.as_view(), name='accounts'),
    path('accounts/create/', adminapp.AccountCreateView.as_view(), name='create_account'),
    path('accounts/edit/<int:pk>/', adminapp.AccountEditView.as_view(), name='edit_account'),
    path('accounts/delete/<int:pk>/', adminapp.AccountDeleteView.as_view(), name='delete_account'),
    path('cabinets/create/', adminapp.CabinetCreateView.as_view(), name='create_cabinet'),
    path('cabinets/edit/<int:pk>/', adminapp.CabinetEditView.as_view(), name='edit_cabinet'),
    path('cabinets/delete/<int:pk>/', adminapp.CabinetDeleteView.as_view(), name='delete_cabinet'),
    path('teams/', adminapp.TeamListView.as_view(), name='teams'),
    path('teams/create/', adminapp.TeamCreateView.as_view(), name='create_team'),
    path('teams/edit/<int:pk>/', adminapp.TeamEditView.as_view(), name='edit_team'),
    path('teams/delete/<int:pk>/', adminapp.TeamDeleteView.as_view(), name='delete_team'),
]