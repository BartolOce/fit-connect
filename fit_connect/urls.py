"""
URL configuration for fit_connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('accounts/register', views.RegisterView, name='register'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('post-job/', views.post_job, name='post_job'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.jobs, name='jobs'),
    path('all_jobs/', views.all_jobs, name='jobs_trainer'),
    path('jobs/<int:job_id>/decline/', views.decline_job, name='decline_job'),

    #ispit
    path('topup/', views.top_up, name='top_up'),
    path('all_top_ups/', views.all_top_ups, name='all_top_ups'),
    path('admin_top_up/', views.admin_top_up, name='admin_top_up'),
    path('dispute/', views.dispute_job, name='dispute_job'), 
]
