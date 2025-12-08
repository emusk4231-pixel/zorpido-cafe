from django.contrib import admin
from django.db import transaction
from django.utils import timezone

# Removed imports: Expense, ExpenseCategory (Expense feature removed)
from .models import Payable, Seller, Register, Expense, ExpenseCategory


# REMOVED: @admin.register(Expense) / ExpenseAdmin (Expense feature removed)
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at')
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'amount', 'date', 'created_by', 'created_at')
    list_filter = ('date', 'category')
    search_fields = ('description', 'category__name')
    date_hierarchy = 'date'


@admin.action(description='Mark selected payables as settled')
def settle_payables(modeladmin, request, queryset):
    with transaction.atomic():
        for p in queryset.select_for_update():
            if p.status == 'settled':
                continue
            p.status = 'settled'
            p.updated_at = timezone.now()
            p.save()
            # related_expense reference removed: Expense feature removed

            # Try to credit current open register (cash) when settling
            try:
                reg = Register.objects.filter(is_open=True).order_by('-opened_at').first()
                if reg:
                    reg.cash_total = (reg.cash_total or 0) + (p.amount or 0)
                    # Recalculate closing using recalculate_totals for consistency
                    reg.recalculate_totals()
            except Exception:
                pass


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('seller__name',)
    actions = [settle_payables]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'email')


from .models import PayablePaymentHistory


@admin.register(PayablePaymentHistory)
class PayablePaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'payable', 'amount', 'payment_mode', 'staff', 'created_at')
    list_filter = ('payment_mode', 'created_at')
    search_fields = ('seller__name', 'remark')

