from django.urls import path,include
from . import views
#wan
app_name = 'api'

urlpatterns=[
    path('api/Strength',views.Str)
]