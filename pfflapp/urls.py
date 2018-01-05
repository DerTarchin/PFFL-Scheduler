from django.conf.urls import include, url
from pffl import views

urlpatterns = [
    url(r'^', include('pffl.urls')),
    url(r'^$', views.home),
]