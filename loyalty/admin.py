from django.contrib import admin
from .models import LoyaltyTransaction, LoyaltyProgram


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
	list_display = ('customer', 'transaction_type', 'points', 'created_at')
	list_filter = ('transaction_type', 'created_at')
	search_fields = ('customer__full_name',)


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
	list_display = ('name', 'points_per_rupee', 'redemption_rate', 'is_active')
	list_filter = ('is_active',)
