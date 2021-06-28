from django.urls import path, include
from frontlinerapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/signin/', views.signin, name='signin'),
    path('accounts/user/<slug:username>/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('accounts/admin/<slug:username>/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('accounts/validate_username/', views.validate_username, name='validate_username'),
    path('accounts/<slug:username>/validate_phone/', views.validate_code, name='validate_code'),
    path('accounts/<slug:username>/pay_to_access_dashboard/', views.paywall, name='paywall'),

]