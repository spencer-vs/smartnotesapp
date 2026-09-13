from django.urls import path
from . import views
from .views import NoteListCreate, NoteDeleteView, NoteUpdateView, NoteDetailView,  search_notes, ContactListCreate, create_task, generate_task_schedule, validate_task_schedule, task_detail, get_all_task, update_task_item, delete_task,  upload_audio, generate_lecture_note, get_all_lectures, get_lecture_detail, lecture_status, generate_tutorial, search_lectures, search_tasks, delete_lectures, get_all_tutorials, get_tutorial_details, delete_tutorial, send_reset_email, reset_password, test_email, request_password_reset, search_tutorials, subscription_status, initialize_payment, verify_payment, paystack_webhook, cancel_subscription, generate_quiz_view, submit_quiz_view, review_quiz_view, saved_quizzes_view, retake_quiz_view, get_active_task

urlpatterns = [
   path("notes/", NoteListCreate.as_view(), name="note_list_create"),
   path("notes/<int:pk>/delete/", NoteDeleteView.as_view(), name="delete_note"),
   path("notes/<int:pk>/update/", NoteUpdateView.as_view(), name="update_note"),
   path("notes/<int:pk>/", NoteDetailView.as_view(), name="note-detail"),
   path("notes/search/", search_notes),
   path("notes/search_lectures/", search_lectures),
   path("notes/search_tasks/", search_tasks),
   path("notes/search_tutorials/", search_tutorials),
   path("notes/contact/", ContactListCreate.as_view(), name="contact_us"),
   path('notes/tasks/create/', views.create_task, name='create_task'),
   path('notes/tasks/active/', views.get_active_task, name='get_active_task'),
   path('notes/tasks/<int:id>/', views.task_detail, name='task_detail'),
   path('notes/tasks/', views.get_all_task, name='get_all_task'),
    path('notes/tasks/<int:task_id>/items/<int:item_id>/', views.update_task_item, name='update_task_item'),
   path('notes/tasks/<int:id>/delete/', views.delete_task, name='delete_task'),
   path('notes/upload-audio/', upload_audio),
   path('notes/generate_lecture_note', generate_lecture_note),
   path("notes/lectures/", get_all_lectures, name="get_all_lectures"),
   path("notes/lectures/<int:id>/", get_lecture_detail, name="lecture-detail"),
   path("notes/lectures/<int:id>/status/", lecture_status),
   path("notes/generate_tutorials/", generate_tutorial, name="generate_tutorial"),
   path("notes/lectures/<int:id>/delete/", delete_lectures, name="delete_lectures"),
   path("notes/tutorials/", get_all_tutorials, name="get_tutorials"),
   path("notes/tutorial/<int:id>/", get_tutorial_details, name="get_tutorial_details"),
   path("notes/tutorial/<int:id>/delete/", delete_tutorial, name="delete_tutorial"),
   path("notes/quizzes/generate/", generate_quiz_view, name="generate_quiz"),
   path("notes/quizzes/<int:quiz_id>/submit/", submit_quiz_view, name="submit_quiz"),
   path("notes/quizzes/<int:quiz_id>/review/", review_quiz_view, name="review_quiz"),
   path("notes/quizzes/", saved_quizzes_view, name="saved_quizzes"),
   path("notes/quizzes/<int:quiz_id>/retake/", retake_quiz_view, name="retake_quiz"),
   path("auth/forgot-password/", request_password_reset),
   path("auth/reset-password/<uidb64>/<token>/", reset_password),
   path("test-email/", test_email, name="test_email"),
   path("subscription/", views.subscription_status),
   path("subscription/cancel/", cancel_subscription, name="cancel-subscription"),
   path("payment/initialize_payment/", initialize_payment, name="initialize-payment"),
   path("payment/verify/<str:reference>/", verify_payment, name='verify-payment'),
   path("payment/paystack_webhook/", paystack_webhook, name="paystack-webhook"),
  
   
   
]





# api.get(`notes/task/${id}/`)