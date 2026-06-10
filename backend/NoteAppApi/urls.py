from django.urls import path
from . import views
from .views import NoteListCreate, NoteDeleteView, NoteUpdateView, NoteDetailView, get_all_task, task_detail, search_notes, ContactListCreate, create_task, update_task, upload_audio, generate_lecture_note, get_all_lectures, get_lecture_detail, lecture_status, generate_tutorial, search_lectures, search_tasks, delete_lectures, delete_task, get_all_tutorials, get_tutorial_details, delete_tutorial, send_reset_email, reset_password, test_email, request_password_reset

urlpatterns = [
   path("notes/", NoteListCreate.as_view(), name="note_list_create"),
   path("notes/<int:pk>/delete/", NoteDeleteView.as_view(), name="delete_note"),
   path("notes/<int:pk>/update/", NoteUpdateView.as_view(), name="update_note"),
   path("notes/<int:pk>/", NoteDetailView.as_view(), name="note-detail"),
   path("notes/search/", search_notes),
   path("notes/search_lectures/", search_lectures),
   path("notes/search_tasks/", search_tasks),
   path("notes/contact/", ContactListCreate.as_view(), name="contact_us"),
   path("notes/task/", views.create_task, name="task_create"),
   path("notes/task/<int:id>/", task_detail, name="task-detail"),
   path("notes/tasks/", get_all_task, name="get_all_tasks"),
   path("notes/task/<int:id>/update/", update_task, name="update-task"), 
   path('notes/upload-audio/', upload_audio),
   path('notes/generate_lecture_note', generate_lecture_note),
   path("notes/lectures/", get_all_lectures, name="get_all_lectures"),
   path("notes/lectures/<int:id>/", get_lecture_detail, name="lecture-detail"),
   path("notes/lectures/<int:id>/status/", lecture_status),
   path("notes/generate_tutorials/", generate_tutorial, name="generate_tutorial"),
   path("notes/lectures/<int:id>/delete/", delete_lectures, name="delete_lectures"),
   path("notes/task/<int:id>/delete/", delete_task, name="delete_task"),
   path("notes/tutorials/", get_all_tutorials, name="get_tutorials"),
   path("notes/tutorial/<int:id>/", get_tutorial_details, name="get_tutorial_details"),
   path("notes/tutorial/<int:id>/delete/", delete_tutorial, name="delete_tutorial"),
   path("auth/forgot-password/", request_password_reset),
   path("auth/reset-password/<uidb64>/<token>/", reset_password),
   path("test-email/", test_email, name="test_email"),
   
]



# api.get(`notes/task/${id}/`)