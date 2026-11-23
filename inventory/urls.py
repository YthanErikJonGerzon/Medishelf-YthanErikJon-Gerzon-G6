from django.urls import path
from . import views

urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('add/', views.medicine_create, name='medicine_create'),
    path('<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('batches/add/', views.batch_create, name='batch_create'),
    path('transactions/new/', views.record_transaction, name='record_transaction'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),
]