from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^(?P<event_id>[0-9]+)', views.show_event, name='show_event'),
    url(r'^$', views.list_all, name='list_all'),
]

