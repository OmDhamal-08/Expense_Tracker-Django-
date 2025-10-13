from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Transaction, Category, Budget
from django.utils import timezone
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    
    class Meta:
        fields = ['username', 'password', 'remember_me']

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user) | Category.objects.filter(is_default=True)
    
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'date', 'description', 'transaction_type', 'recurring', 'recurrence_frequency']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class BudgetForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user) | Category.objects.filter(is_default=True)
    
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TransactionFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)
    transaction_type = forms.ChoiceField(choices=Transaction.TRANSACTION_TYPES, required=False)
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user) | Category.objects.filter(is_default=True)