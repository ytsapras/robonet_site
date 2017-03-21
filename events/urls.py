from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    #url(r'^add_operator/$', views.add_operator, name='add_operator'),
    #url(r'^simple.png$', views.simple),
    #url(r'^test/$', views.test, name='test'),
    url(r'^event/(?P<event_name>[\w-]+)', views.show_event, name='show_event'),
    url(r'^download_lc/(?P<event_name>[\w-]+)', views.download_lc, name='download_lc'),
    url(r'^event_by_id/(?P<event_id>[0-9]+)', views.show_event_by_id, name='show_event_by_id'),
    url(r'^download_lc_by_id/(?P<event_id>[0-9]+)', views.download_lc_by_id, name='download_lc_by_id'),
    url(r'^obs_log/(?P<date>[0-9]+)', views.obs_log, name='obs_log'),
    url(r'^obs_details/(?P<event_name>[\w-]+)', views.event_obs_details, name='event_obs_details'),
    url(r'^tap/', views.tap, name='tap'),
    url(r'^list_all/', views.list_all, name='list_all'),
    url(r'^$', views.dashboard, name='dashboard'),
]
