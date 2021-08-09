import debug_toolbar
from django.urls import path, include

urlpatterns = [
    path('', include('frontlinerapp.urls')),
    path("ref/", include("pinax.referrals.urls", namespace="pinax_referrals")),
    path('__debug__/', include(debug_toolbar.urls)),

]
