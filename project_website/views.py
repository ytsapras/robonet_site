from django.conf import settings
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
import sys, os

local_path = os.getcwd()+'/project_website/templates/project_website/'

# Create your views here.
def home_html(request):
    return rende(local_path+'home.html')

def research_html(request):
    return render(local_path+'research.html')

def publications_html(request):
    return render(local_path+'publications.html')

def group_html(request):
    return render(local_path+'group.html')

def authors_html(request):
    return render(local_path+'authors.html')

def release_html(request):
    return render(local_path+'release.html')

def naming_html(request):
    return render(local_path+'naming.html')

def options_html(request):
    return render(local_path+'options.html')

def calendar_html(request):
    return render(local_path+'calendar.html')

def docs_html(request):
    return render(local_path+'documentation.html')
