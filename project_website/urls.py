from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
   url(r'^home/', views.home_html, name='home_html'),
   url(r'^release/', views.release_html, name='release_html'),
   url(r'^naming/', views.naming_html, name='naming_html'),
   url(r'^options/', views.options_html, name='options_html'),
   url(r'^research/', views.research_html, name='research_html'),
   url(r'^publications/', views.publications_html, name='publications_html'),
   url(r'^group/', views.group_html, name='group_html'),
   url(r'^authors/', views.authors_html, name='authors_html'),
   url(r'^calendar/', views.calendar_html, name='calendar_html'),
   url(r'^documentation', views.docs_html, name='docs_html'),
]

