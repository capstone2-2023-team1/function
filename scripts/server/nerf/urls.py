from django.urls import path
from . import views

app_name='nerf'

urlpatterns=[
   path('trans/', views.trans, name='trans'),
]
