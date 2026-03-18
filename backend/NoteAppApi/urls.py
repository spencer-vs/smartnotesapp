from django.urls import path
from . import views
from .views import NoteListCreate, NoteDeleteView, NoteUpdateView, NoteDetailView, task_detail, search_notes, ContactListCreate, create_task

urlpatterns = [
   path("notes/", NoteListCreate.as_view(), name="note_list_create"),
   path("notes/<int:pk>/delete/", NoteDeleteView.as_view(), name="delete_note"),
   path("notes/<int:pk>/update/", NoteUpdateView.as_view(), name="update_note"),
   path("notes/<int:pk>/", NoteDetailView.as_view(), name="note-detail"),
   path("notes/search/", search_notes),
   path("notes/contact/", ContactListCreate.as_view(), name="contact_us"),
   path("notes/task/", views.create_task, name="task_create"),
   path("notes/task/<int:pk>/", task_detail, name="task-detail")
]


# api.get(`notes/task/${id}/`)