from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login 

from .models import Transaction, Category, Budget
from .forms import (UserRegisterForm, UserLoginForm, TransactionForm, 
                   CategoryForm, BudgetForm, TransactionFilterForm,AuthenticationForm)

import matplotlib
matplotlib.use('Agg')  # Required for backend rendering
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from django.db.models import Sum
import seaborn as sns

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        print("Form is valid?", form.is_valid())  # Debug
        print("Form errors:", form.errors)  # Debug
        
        if form.is_valid():
            user = form.save()
            print("User created:", user.username)  # Debug
            messages.success(request, 'Registration successful!')
            return redirect('login')  # Redirect to login page
        else:
            # Display errors in the template
            return render(request, 'expenses/register.html', {
                'form': form,
                'errors': form.errors  # Pass errors to template
            })
    else:
        form = UserRegisterForm()
    
    return render(request, 'expenses/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = UserLoginForm()
    
    return render(request, 'expenses/login.html', {'form': form})

# Dashboard View
@login_required
def home(request):
    return render(request, 'expenses/home.html')

def dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Calculate totals
    income = Transaction.objects.filter(
        user=request.user, 
        transaction_type='IN',
        date__range=[start_of_month, end_of_month]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expenses = Transaction.objects.filter(
        user=request.user, 
        transaction_type='EX',
        date__range=[start_of_month, end_of_month]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    balance = income - expenses
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Budget alerts
    budgets = Budget.objects.filter(user=request.user, is_active=True)
    budget_alerts = []
    
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='EX',
            date__range=[budget.start_date, budget.end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if spent > budget.amount:
            budget_alerts.append({
                'category': budget.category,
                'budget': budget.amount,
                'spent': spent,
                'overspent': spent - budget.amount
            })
    
    context = {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'budget_alerts': budget_alerts,
    }
    
    return render(request, 'expenses/dashboard.html', context)

# Transaction Views
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'expenses/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user).order_by('-date')
        
        # Filtering
        form = TransactionFilterForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('start_date'):
                queryset = queryset.filter(date__gte=data['start_date'])
            if data.get('end_date'):
                queryset = queryset.filter(date__lte=data['end_date'])
            if data.get('category'):
                queryset = queryset.filter(category=data['category'])
            if data.get('transaction_type'):
                queryset = queryset.filter(transaction_type=data['transaction_type'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TransactionFilterForm(self.request.GET or None, user=self.request.user)
        return context

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('transaction-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('transaction-list')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('transaction-list')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(Q(user=self.request.user) | Q(is_default=True)).order_by('name')

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('category-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('category-list')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

# Budget Views
class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'expenses/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).order_by('-start_date')

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    success_url = reverse_lazy('budget-list')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


# Export Data
@login_required
def export_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    # Create DataFrame
    df = pd.DataFrame.from_records(transactions.values(
        'date', 'amount', 'transaction_type', 'category__name', 'description'
    ))
    
    # Rename columns
    df = df.rename(columns={
        'date': 'Date',
        'amount': 'Amount',
        'transaction_type': 'Type',
        'category__name': 'Category',
        'description': 'Description'
    })
    
    # Map transaction types
    df['Type'] = df['Type'].map({'IN': 'Income', 'EX': 'Expense'})
    
    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    # Write DataFrame to CSV
    df.to_csv(response, index=False)
    
    return response

# Recurring Transactions
@login_required
def process_recurring_transactions(request):
    today = timezone.now().date()
    recurring_transactions = Transaction.objects.filter(
        user=request.user,
        recurring=True,
        next_recurrence_date__lte=today
    )
    
    created_count = 0
    
    for transaction in recurring_transactions:
        # Create new transaction
        new_transaction = Transaction.objects.create(
            user=request.user,
            amount=transaction.amount,
            category=transaction.category,
            date=today,
            description=transaction.description,
            transaction_type=transaction.transaction_type,
            recurring=True,
            recurrence_frequency=transaction.recurrence_frequency
        )
        
        # Update next recurrence date
        if transaction.recurrence_frequency == 'daily':
            transaction.next_recurrence_date = today + timedelta(days=1)
        elif transaction.recurrence_frequency == 'weekly':
            transaction.next_recurrence_date = today + timedelta(weeks=1)
        elif transaction.recurrence_frequency == 'monthly':
            transaction.next_recurrence_date = today + timedelta(days=30)
        elif transaction.recurrence_frequency == 'yearly':
            transaction.next_recurrence_date = today + timedelta(days=365)
        
        transaction.save()
        created_count += 1
    
    messages.success(request, f'Processed {created_count} recurring transactions.')
    return redirect('dashboard')

# Search Functionality
@login_required
def search_transactions(request):
    query = request.GET.get('q', '')
    
    if query:
        transactions = Transaction.objects.filter(
            Q(user=request.user) &
            (Q(description__icontains=query) |
             Q(category__name__icontains=query) |
             Q(amount__icontains=query))
        ).order_by('-date')
    else:
        transactions = Transaction.objects.none()
    
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'expenses/search_results.html', {
        'transactions': page_obj,
        'query': query
    })

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Make sure you have a URL named 'login




@login_required
def reports(request):
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
    
    # Get transactions in date range
    transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Prepare data for charts - ensure all required fields are included
    df = pd.DataFrame.from_records(transactions.values(
        'date', 'amount', 'transaction_type', 'category__name'
    ))
    
    # Handle empty DataFrame case
    if df.empty:
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'time_series_chart': None,
            'category_pie': None,
            'monthly_expenses_chart': None,
            'category_expenses_chart': None,
            'no_data': True
        }
        return render(request, 'expenses/reports.html', context)
    
    # Ensure transaction_type exists before processing
    if 'transaction_type' not in df.columns:
        df['transaction_type'] = 'EX'  # Default to expense if missing
    
    # ========== PLOTLY CHARTS (Existing) ==========
    
    # Income vs Expense over time (line chart)
    try:
        df['date'] = pd.to_datetime(df['date'])
        time_series = df.groupby(['date', 'transaction_type'])['amount'].sum().unstack().fillna(0)
        time_series_chart = px.line(
            time_series.reset_index(), 
            x='date', 
            y=['IN', 'EX'],
            labels={'value': 'Amount', 'variable': 'Type', 'date': 'Date'},
            title='Income vs Expenses Over Time'
        ) if 'IN' in time_series.columns and 'EX' in time_series.columns else None
    except Exception as e:
        time_series_chart = None
    
    # Expense by category (pie chart)
    try:
        expenses_df = df[df['transaction_type'] == 'EX'] if 'transaction_type' in df.columns else pd.DataFrame()
        category_pie = px.pie(
            expenses_df,
            values='amount',
            names='category__name',
            title='Expenses by Category'
        ) if not expenses_df.empty else None
    except Exception as e:
        category_pie = None
    
    # ========== MATPLOTLIB CHARTS (New) ==========
    
    # Monthly Expenses Bar Chart
    try:
        # Create monthly data
        monthly_data = transactions.extra({
            'month': "EXTRACT(month FROM date)",
            'year': "EXTRACT(year FROM date)"
        }).values('year', 'month').annotate(
            income=Sum('amount', filter=Q(transaction_type='IN')),
            expenses=Sum('amount', filter=Q(transaction_type='EX'))
        ).order_by('year', 'month')
        
        if monthly_data:
            months = []
            income_data = []
            expenses_data = []
            
            for data in monthly_data:
                month_year = f"{int(data['month'])}/{int(data['year'])}"
                months.append(month_year)
                income_data.append(float(data['income'] or 0))
                expenses_data.append(float(data['expenses'] or 0))
            
            # Create matplotlib bar chart
            plt.figure(figsize=(12, 6))
            x = range(len(months))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], income_data, width, label='Income', color='#28a745', alpha=0.8)
            plt.bar([i + width/2 for i in x], expenses_data, width, label='Expenses', color='#dc3545', alpha=0.8)
            
            plt.title('Monthly Income vs Expenses', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.xticks(x, months, rotation=45)
            plt.legend()
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            monthly_expenses_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
        else:
            monthly_expenses_chart = None
            
    except Exception as e:
        monthly_expenses_chart = None
    
    # Category Expenses Pie Chart
    try:
        category_data = transactions.filter(transaction_type='EX').values(
            'category__name'
        ).annotate(total=Sum('amount')).order_by('-total')
        
        if category_data:
            categories = []
            amounts = []
            
            for data in category_data:
                categories.append(data['category__name'] or 'Uncategorized')
                amounts.append(float(data['total']))
            
            # Create matplotlib pie chart
            plt.figure(figsize=(10, 8))
            
            # Use a color palette
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            # Improve text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Expenses by Category', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            category_expenses_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
        else:
            category_expenses_chart = None
            
    except Exception as e:
        category_expenses_chart = None
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'time_series_chart': time_series_chart,
        'category_pie': category_pie,
        'monthly_expenses_chart': monthly_expenses_chart,
        'category_expenses_chart': category_expenses_chart,
        'no_data': False
    }
    
    return render(request, 'expenses/reports.html', context)

@login_required
def about(request):
    return render(request,'expenses/about.html')
