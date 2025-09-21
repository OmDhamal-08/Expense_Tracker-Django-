from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ('user', 'name')
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    INCOME = 'IN'
    EXPENSE = 'EX'
    TRANSACTION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
    recurring = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(max_length=20, blank=True, null=True)  # daily, weekly, monthly, yearly
    next_recurrence_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.date}"
    
    def get_absolute_url(self):
        return reverse('transaction-detail', kwargs={'pk': self.pk})

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'category', 'start_date', 'end_date')
    
    def __str__(self):
        return f"{self.category} - {self.amount} ({self.start_date} to {self.end_date})"