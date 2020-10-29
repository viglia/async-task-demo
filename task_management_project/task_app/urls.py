from django.urls import path, include, re_path
from task_app import views

urlpatterns = [

    path("jobs",
         views.JobList.as_view(),
         name="job-list"),

    path("jobs/<int:pk>",
         views.JobDetail.as_view(),
         name="job-detail")
]