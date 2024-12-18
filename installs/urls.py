from django.urls import path
import installs.views as installs

app_name = 'installs'

urlpatterns = [
    path('register_install/', installs.register_install, name='register_install'),
    path('change_install/', installs.change_install, name='change_install'),
    path('get_installs/', installs.get_installs, name='get_installs'),
    path('make_push/', installs.make_push, name='make_push'),
    path('execute_push/', installs.execute_push, name='execute_push'),
    path('make_test_push/', installs.make_test_push, name='make_test_push'),
    path('execute_test_push/', installs.execute_test_push, name='execute_test_push'),
    path('check_push_audience/', installs.check_push_audience, name='check_push_audience'),
    path('applications/', installs.AppListView.as_view(), name='applications'),
    path('applications/create/', installs.AppCreateView.as_view(), name='create_application'),
    path('applications/edit/<int:pk>/', installs.AppEditView.as_view(), name='edit_application'),
    path('applications/delete/<int:pk>/', installs.AppDeleteView.as_view(), name='delete_application'),
    path('pushes/', installs.PushListView.as_view(), name='pushes'),
    path('pushes/edit/<int:pk>/', installs.PushEditView.as_view(), name='edit_push'),
    path('pushes/delete/<int:pk>/', installs.PushDeleteView.as_view(), name='delete_push'),
]
