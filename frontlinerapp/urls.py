from django.urls import path, include
from frontlinerapp import views

urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/signin/', views.signin, name='signin'),
    path('accounts/terms-and-conditions/', views.terms, name='terms'),

    path('accounts/user/<slug:username>/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('accounts/user/<slug:username>/dashboard/messages/', views.user_messages, name='user_messages'),
    path('accounts/user/<slug:username>/dashboard/notifications/', views.user_notifications, name='user_notifications'),

    path('accounts/admin/<slug:username>/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('accounts/admin/<slug:username>/dashboard/messages/', views.admin_messages, name='admin_messages'),
    path('accounts/admin/<slug:username>/dashboard/messages/<int:id>/', views.admin_messages_details, name='message_details'),
    path('accounts/admin/<slug:username>/dashboard/notifications/', views.admin_notifications, name='admin_notifications'),
    path('accounts/admin/<slug:username>/dashboard/user_management/', views.user_management, name='user_management'),
    path('accounts/admin/<slug:username>/dashboard/user_management/<slug:user>', views.user_details, name='user_details'),
    path('accounts/admin/<slug:username>/dashboard/search_users/', views.search_users, name='search_users'),
    path('accounts/admin/<slug:username>/dashboard/settings/', views.admin_settings, name='admin_settings'),

    path('accounts/chat/', views.chat_admin, name='chat_admin'),
    path('accounts/reply/', views.reply_admin, name='reply_admin'),
    path('accounts/validate_username/', views.validate_username, name='validate_username'),
    path('accounts/delete_users/', views.delete_users, name='delete_users'),
    path('accounts/validate_login/', views.validate_login, name='validate_login'),
    path('accounts/<slug:username>/validate_phone/', views.validate_code, name='validate_code'),
    path('accounts/<slug:username>/pay_to_access_dashboard/', views.paywall, name='paywall'),

    path('ajax/latest_message/', views.get_latest_message, name='get_latest_message'),


]