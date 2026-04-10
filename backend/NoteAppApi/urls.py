from django.urls import path
from . import views
from .views import NoteListCreate, NoteDeleteView, NoteUpdateView, NoteDetailView, get_all_task, task_detail, search_notes, ContactListCreate, create_task, update_task, upload_audio, generate_lecture_note, get_all_lectures, get_lecture_detail, lecture_status, generate_tutorial, search_lectures, search_tasks, delete_lectures, delete_task

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
   path("notes/tutorials/", generate_tutorial, name="generate_tutorial"),
   path("notes/<int:id>/delete_lectures/", delete_lectures, name="delete_lectures"),
   path("notes/<int:id>/delete_task/", delete_task, name="delete_task")
]


# api.get(`notes/task/${id}/`)