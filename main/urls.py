from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('applicant/<int:user_id>/', views.view_applicant_profile, name='view_applicant_profile'),
    path('employer/<int:user_id>/', views.view_employer_profile, name='view_employer_profile'),
    path('employer/applications/', views.employer_applications, name='employer_applications'),
    path('media/<path:path>', views.PDFView.as_view(), name='pdf_viewer'),
] 