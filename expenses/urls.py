from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .views import (TransactionListView, TransactionDetailView, TransactionCreateView,
                   TransactionUpdateView, TransactionDeleteView, CategoryListView,
                   CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
                   BudgetListView, BudgetCreateView, BudgetUpdateView, BudgetDeleteView)

urlpatterns = [
       # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    path('home/', views.home, name='home'),
    # Password Change URLs - ADD THESE
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='expenses/password_change.html',
             success_url=reverse_lazy('password_change_done')
         ),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='expenses/password_change_done.html'
         ),
         name='password_change_done'),
    
    # Password Reset URLs (your existing ones)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='expenses/password_reset.html',
             email_template_name='expenses/password_reset_email.html',
             subject_template_name='expenses/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='expenses/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='expenses/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='expenses/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/add/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    
    # Budgets
    path('budgets/', BudgetListView.as_view(), name='budget-list'),
    path('budgets/add/', BudgetCreateView.as_view(), name='budget-create'),
    path('budgets/<int:pk>/edit/', BudgetUpdateView.as_view(), name='budget-update'),
    path('budgets/<int:pk>/delete/', BudgetDeleteView.as_view(), name='budget-delete'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Export
    path('export/', views.export_transactions, name='export-transactions'),
    
    # Recurring transactions
    path('process-recurring/', views.process_recurring_transactions, name='process-recurring'),
    
    # Search
    path('search/', views.search_transactions, name='search-transactions'),
    path('about/', views.about, name='about'),
]