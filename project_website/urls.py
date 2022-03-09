from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
   path('', views.home_html, name='home_html'),
   path('release/', views.release_html, name='release_html'),
   path('naming/', views.naming_html, name='naming_html'),
   path('options/', views.options_html, name='options_html'),
   path('research/', views.research_html, name='research_html'),
   path('publications/', views.publications_html, name='publications_html'),
   path('group/', views.group_html, name='group_html'),
   path('authors/', views.authors_html, name='authors_html'),
   path('calendar/', views.calendar_html, name='calendar_html'),
   path('documentation/', views.docs_html, name='docs_html'),
]
