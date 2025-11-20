from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from .models import Expense, Payable, Seller, Register


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'amount', 'payment_status', 'payment_mode', 'seller', 'staff', 'created_at')
    list_filter = ('payment_status', 'payment_mode', 'created_at')
    search_fields = ('description', 'seller__name')


@admin.action(description='Mark selected payables as settled')
def settle_payables(modeladmin, request, queryset):
    with transaction.atomic():
        for p in queryset.select_for_update():
            if p.status == 'settled':
                continue
            p.status = 'settled'
            p.updated_at = timezone.now()
            p.save()
            # Update related expense
            try:
                exp = p.related_expense
                if exp:
                    exp.payment_status = 'paid'
                    exp.save()
            except Exception:
                pass

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
    list_display = ('id', 'seller', 'amount', 'status', 'related_expense', 'created_at', 'updated_at')
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
from django.contrib import admin

# Register your models here.
