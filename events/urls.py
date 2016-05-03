from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^simple.png$', views.simple),
    url(r'^test/$', views.test, name='test'),
    url(r'^(?P<event_id>[0-9]+)', views.show_event, name='show_event'),
    url(r'^obs_log/(?P<date>[0-9]+)', views.obs_log, name='obs_log'),
    url(r'^obs_details/(?P<event_id>[0-9]+)', views.event_obs_details, name='event_obs_details'),
    url(r'^$', views.list_all, name='list_all'),
]

