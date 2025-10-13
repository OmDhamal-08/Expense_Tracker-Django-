from django.contrib import admin
from .models import Transaction, Category, Budget

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date', 'transaction_type')
    list_filter = ('transaction_type', 'date', 'category')
    search_fields = ('description', 'category__name')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name',)

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('category__name',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Budget, BudgetAdmin)