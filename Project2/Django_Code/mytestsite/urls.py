"""mytestsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from application.views import login
from application.views import API13
from application.views import API12
from application.views import API11
from application.views import API10
from application.views import API9
from application.views import API8
from application.views import API7
from application.views import API6
from application.views import API5
from application.views import API4
from application.views import API3
from application.views import API2
from application.views import API1
from application.views import API0
from application.views import outputAPI

urlpatterns = [
    path('login/', admin.site.urls),
    path('', login),
    # path('user/', include('application.urls')),
    path('API1/',API1,name='API1'),
    path('API13/',API13,name='API13'),
    path('API12/',API12,name='API12'),
    path('API11/', API11),
    path('API10/',API10),
    path('API9/',API9),
    path('API8/',API8),
    path('API7/',API7),
    path('API6/',API6),
    path('API5/',API5),
    path('API4/',API4),
    path('API3/',API3),
    path('API2/',API2),
    path('API1/',API1,name='API1'),
    path('API0/',API0),
    path('API/',outputAPI,name='API')






]
