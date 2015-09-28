from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list_all/', views.list_all, name='list_all'),
    url(r'^$', views.index, name='index'),
]

