from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    #url(r'^simple.png$', views.simple),
    #url(r'^test/$', views.test, name='test'),
    url(r'^login/$', auth_views.login, {'template_name':'events/registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'/'}, name='logout'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^event/(?P<event_name>[\w-]+)', views.show_event, name='show_event'),
    url(r'^download_lc/(?P<event_name>[\w-]+)', views.download_lc, name='download_lc'),
    url(r'^event_by_id/(?P<event_id>[0-9]+)', views.show_event_by_id, name='show_event_by_id'),
    url(r'^download_lc_by_id/(?P<event_id>[0-9]+)', views.download_lc_by_id, name='download_lc_by_id'),
    url(r'^obs_log/(?P<date>[0-9]+)', views.obs_log, name='obs_log'),
    url(r'^obs_requests24/$', views.obs_requests24, name='obs_requests24'),
    url(r'^active_obs_requests/$', views.active_obs_requests, name='active_obs_requests'),
    url(r'^obs_monitor/$', views.display_obs_monitor, name='obs_monitor'),
    url(r'^obs_details/(?P<event_name>[\w-]+)', views.event_obs_details, name='event_obs_details'),
    url(r'^query_obs_requests/$', views.query_obs_requests, name='query_obs_requests'),
    url(r'^query_obs_by_date/timestamp=(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&time_expire=(?P<time_expire>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&request_status=(?P<request_status>[A-Z][A-Z])/$', views.query_obs_by_date, name='query_obs_by_date'),
    url(r'^record_obs_request/$', views.record_obs_request, name='record_obs_requests'),
    url(r'^record_sub_obs_request/sr_id=(?P<sr_id>[0-9]+)&grp_id=(?P<grp_id>[A-Za-z0-9]+.[0-9]+)&track_id=(?P<track_id>[0-9]+)&window_start=(?P<window_start>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&window_end=(?P<window_end>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&status=(?P<status>[A-Z_]+)/$', views.record_sub_obs_request, name='record_sub_obs_request'),
    url(r'^record_sub_obs_request/sr_id=(?P<sr_id>[0-9]+)&grp_id=(?P<grp_id>[A-Za-z0-9]+.[0-9]+)&track_id=(?P<track_id>[0-9]+)&window_start=(?P<window_start>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&window_end=(?P<window_end>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})&status=(?P<status>[A-Z_]+)&time_executed=(?P<time_executed>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/$', views.record_sub_obs_request, name='record_sub_obs_request'),
    url(r'^record_data_file/$', views.record_data_file, name='record_data_file'),
    url(r'^add_operator/$', views.add_operator, name='add_operator'),
    url(r'^add_telescope/$', views.add_telescope, name='add_telescope'),
    url(r'^add_event/$', views.add_event, name='add_event'),
    url(r'^add_eventname/$', views.add_eventname, name='add_eventname'),
    url(r'^add_singlemodel/$', views.add_singlemodel, name='add_singlemodel'),
    url(r'^add_binarymodel/$', views.add_binarymodel, name='add_binarymodel'),
    url(r'^add_eventreduction/$', views.add_eventreduction, name='add_eventreduction'),
    url(r'^add_tap/$', views.add_tap, name='add_tap'),
    url(r'^add_taplima/$', views.add_taplima, name='add_taplima'),
    url(r'^add_datafile/$', views.add_datafile, name='add_datafile'),
    url(r'^add_image/$', views.add_image, name='add_image'),
    url(r'^tap/', views.tap, name='tap'),
    url(r'^set_tap_status/', views.set_tap_status, name='set_tap_status'),
    url(r'^set_event_status/', views.set_event_status, name='set_event_status'),
    url(r'^list_year/(?P<year>[0-9]+)', views.list_year, name='list_year'),
    url(r'^list_all/', views.list_all, name='list_all'),
    url(r'^display_fields/', views.display_fields, name='display_fields'),
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^quality_control/$', views.data_quality_control, name='data_quality_control'),
    url(r'^test_token/$',views.test_token, name='test_token'),
]
