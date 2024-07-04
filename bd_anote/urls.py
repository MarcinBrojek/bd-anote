"""bd_anote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from anote import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login, name='login'),
    path('login/', views.login, name='login'),

    path('login/remind-password/', views.remind, name='remind'),

    path('login/register/', views.register, name='register'),

    path('profile/', views.profile, name='profile'),

    path('profile/change-password/', views.change, name='change'),

    path('profile/logout/', views.logout, name='logout'),

    path('profile/classes/', views.classes, name='classes'),

    path('profile/watched/', views.watched, name='watched'),
    path('profile/watched/remove/<int:observ_id>/', views.watched_remove, name='watched_remove'),

    path('profile/add-subject/', views.add_subject, name='add_subject'),

    path('profile/add-classes/', views.add_classes, name='add_classes'),

    path('profile/classes/<int:classes_id>/', views.class_note, name='class_note'),

    path('profile/classes/<int:classes_id>/edition/', views.edit_note, name='edit_note'),
    path('profile/classes/<int:classes_id>/publish/', views.publish_note, name='publish_note'),
    path('profile/classes/<int:classes_id>/corrections/', views.note_corrections, name='note_corrections'),
    path('profile/classes/<int:classes_id>/reset/', views.note_reset, name='note_reset'),
    path('profile/classes/<int:classes_id>/delete/', views.class_delete, name='class_delete'),
    path('profile/classes/<int:classes_id>/declare/', views.note_declare, name='note_declare'),
    path('profile/classes/<int:classes_id>/resign/', views.note_resign, name='note_resign'),
    
    path('profile/classes/<int:classes_id>/correction/add/', views.add_correction, name='add_correction'),
    path('profile/classes/<int:classes_id>/correction/preview/<int:correction_id>/', views.correction_preview, name='correction_preview'),
    path('profile/classes/<int:classes_id>/correction/accept/<int:correction_id>/', views.accept_correction, name='accept_correction'),
    path('profile/classes/<int:classes_id>/correction/reject/<int:correction_id>/', views.reject_correction, name='reject_correction'),
    
    path('note/<int:note_id>/pdf_note/', views.pdf_note, name='pdf_note'),
    path('note/<int:note_id>/download/', views.note_download, name='note_download'),
    
    path('correction/<int:correction_id>/pdf_note/', views.pdf_correction, name='pdf_correction'),
    path('correction/<int:correction_id>/download/', views.correction_download, name='correction_download'),
    path('correction/<int:correction_id>/remove/', views.correction_remove, name='correction_remove'),
    
    path('profile/my-notes/', views.notes, name='notes')
]
