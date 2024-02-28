from django.urls import path
from .views import *

urlpatterns = [
    path('index/', base, name='index'),
    path('graph/', graph, name='graph'),
    path('tabel_plan/', tabelPlan, name="tabelPlan"),
    path('tabel_fact_update', tabelFactUpdate, name="tabelFactUpdate"),
    path('tabel_fact_read/', tabel_fact_read, name="tabelFactRead"),
    path('',home,name='home'),
    path('login/',login_user,name='login'),
    path('logout/',logout_user,name='logout'),
    path('tabel_fact_update/', tabelFactUpdate, name="tabelFactUpdate"),


]