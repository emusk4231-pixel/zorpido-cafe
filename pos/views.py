"""POS views: dashboard, orders, payments, inventory, credit and register management.

This module provides the core POS functionality including:
- Inventory management (stock updates, low stock alerts)
- Customer credit tracking (balance updates, transaction history) 
- Order processing (creation, payment, completion)
- POS dashboard with sales metrics and register management
"""

from decimal import Decimal, InvalidOperation
import json
from io import BytesIO
import base64
import logging
from typing import Optional

try:
    import qrcode
except ImportError:
    qrcode = None

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Count
from django.db import transaction
from django.utils import timezone
from django.http import FileResponse, HttpResponse
from django.db.models.functions import TruncDate

from users.models import User
from menu.models import MenuItem, Category
from .models import CreditTransaction, Register, Payable
from .models import Seller
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm
from orders.models import Order, OrderItem
# Removed imports: Expense, ExpenseCategory (Expense feature removed)
# Attendance feature removed: Staff/Shift/Attendance models no longer imported


def _get_active_register():
    return Register.objects.filter(is_open=True).order_by('-opened_at').first()


def _require_open_register_json():
    """Return a JsonResponse error if no open register exists (helper for views)."""
    reg = _get_active_register()
    if not reg:
        return JsonResponse({'success': False, 'error': 'No open register. Please open register first.'}, status=400)
    return None


def is_staff_or_admin(user):
    """Check if user is staff/admin"""
    # Accept Django staff/superuser flags as well as legacy user_type == 'staff'
    return bool(
        user and user.is_authenticated and (
            getattr(user, 'user_type', None) == 'staff'
            or getattr(user, 'is_staff', False)
            or getattr(user, 'is_superuser', False)
        )
    )


def is_manager_or_admin(user):
    """Return True if user is manager or superuser (used for sensitive attendance edits)."""
    return bool(
        user and user.is_authenticated and (
            getattr(user, 'is_superuser', False)
            or getattr(user, 'user_type', '') == 'manager'
            or user.has_perm('pos.manage_attendance')
        )
    )





@login_required
@user_passes_test(is_staff_or_admin)
def order_detail(request, order_id):
    """Display order details for viewing/editing"""
    try:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'pos/order_detail.html', {
            'order': order,
            'items': order.items.select_related('menu_item').all()
        })
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('pos:dashboard')


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def create_order(request):
    """Create a new order"""
    try:
        data = json.loads(request.body)

        # Get customer if ID provided
        customer = None
        customer_id = data.get('customer_id')
        if customer_id:
            customer = get_object_or_404(User, id=customer_id, user_type='customer')
        # Ensure a register is open
        err = _require_open_register_json()
        if err:
            return err

        # Create order and persist items (if any)
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                staff=request.user
            )

            items = data.get('items') or []
            # items expected to be list of { item_id, quantity, name?, price? }
            for it in items:
                try:
                    item_id = int(it.get('item_id'))
                    quantity = int(it.get('quantity', 1))
                except Exception:
                    raise ValueError('Invalid item payload')

                if quantity <= 0:
                    raise ValueError('Quantity must be positive')

                menu_item = get_object_or_404(MenuItem, id=item_id)

                # Create OrderItem (OrderItem.save will compute subtotal and update order totals)
                oi = OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    item_name=menu_item.name,
                    item_price=menu_item.price,
                    quantity=quantity
                )

                # Reduce stock
                if hasattr(menu_item, 'reduce_stock'):
                    try:
                        menu_item.reduce_stock(quantity)
                    except Exception:
                        # Non-critical: continue but log
                        logging.exception('Failed to reduce stock for %s', menu_item)
                else:
                    menu_item.stock_quantity = (menu_item.stock_quantity or 0) - quantity
                    menu_item.save()

            # Ensure totals are up-to-date
            order.calculate_totals()

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'total': str(order.total)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def pos_overview(request):
    """Display POS overview with register history and management"""
    # Get register history
    registers = Register.objects.all().order_by('-opened_at')[:30]  # Last 30 registers
    active_register = Register.objects.filter(is_open=True).first()

    # Calculate daily statistics
    today = timezone.localdate()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    # Get today's statistics
    from orders.models import Order
    today_orders = Order.objects.filter(
        completed_at__gte=start_of_day,
        completed_at__lte=end_of_day,
        status='completed'
    )
    today_sales = today_orders.aggregate(
        total=Sum('paid_amount'),
        cash=Sum('paid_amount', filter=Q(payment_method='cash')),
        credit=Sum('paid_amount', filter=Q(payment_method='credit')),
        qr=Sum('paid_amount', filter=Q(payment_method='qr'))
    )

    # compute today's expenses
    try:
        today_expenses_total = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    except Exception:
        today_expenses_total = Decimal('0.00')

    # attach expenses_total to each register by date range
    regs = list(registers)
    for reg in regs:
        start = reg.opened_at.date() if reg.opened_at else today
        end = reg.closed_at.date() if reg.closed_at else today
        try:
            reg.expenses_total = Expense.objects.filter(date__gte=start, date__lte=end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        except Exception:
            reg.expenses_total = Decimal('0.00')
    # set active_register.expenses_total if present
    if active_register:
        try:
            astart = active_register.opened_at.date() if active_register.opened_at else today
            aend = active_register.closed_at.date() if active_register.closed_at else today
            active_register.expenses_total = Expense.objects.filter(date__gte=astart, date__lte=aend).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        except Exception:
            active_register.expenses_total = Decimal('0.00')

    context = {
        'registers': regs,
        'active_register': active_register,
        'today_sales': {
            'total': today_sales['total'] or Decimal('0.00'),
            'cash': today_sales['cash'] or Decimal('0.00'),
            'credit': today_sales['credit'] or Decimal('0.00'),
            'qr': today_sales['qr'] or Decimal('0.00')
        },
        'today_expenses_total': today_expenses_total,
        'total_customers_credit': User.objects.filter(user_type='customer').aggregate(total=Sum('credit_balance'))['total'] or Decimal('0.00')
    }
    # Add outstanding payables total to context
    try:
        context['outstanding_payables_total'] = Payable.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    except Exception:
        context['outstanding_payables_total'] = Decimal('0.00')
    return render(request, 'pos/overview.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def export_pos_overview_pdf(request):
    """Generate a PDF export of the POS overview using reportlab.platypus.

    Accepts optional GET params `from` and `to` in YYYY-MM-DD format to select
    a date range. If omitted, defaults to today.
    """
    try:
        # Import reportlab on demand so the app still loads if the package is missing
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import mm
    except ImportError:
        return HttpResponse('reportlab is not installed. Please pip install reportlab', status=500)

    # Parse date range
    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    today = timezone.localdate()
    try:
        if from_date_str:
            from_date = timezone.datetime.fromisoformat(from_date_str).date()
        else:
            from_date = today
        if to_date_str:
            to_date = timezone.datetime.fromisoformat(to_date_str).date()
        else:
            to_date = today
    except Exception:
        return HttpResponse('Invalid date format. Use YYYY-MM-DD', status=400)

    # Build aware datetimes for DB filtering
    start_dt = timezone.make_aware(timezone.datetime.combine(from_date, timezone.datetime.min.time()))
    end_dt = timezone.make_aware(timezone.datetime.combine(to_date, timezone.datetime.max.time()))

    # Gather data
    orders_qs = Order.objects.filter(status='completed', completed_at__gte=start_dt, completed_at__lte=end_dt)
    sales_agg = orders_qs.aggregate(total=Sum('paid_amount'))
    total_sales = sales_agg['total'] or Decimal('0.00')

    # Expense feature removed: no expenses to include in overview PDF
    total_expenses = Decimal('0.00')

    # Credit transactions: given (add) / recovered (deduct)
    credit_given = CreditTransaction.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt, action='add').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    credit_recovered = CreditTransaction.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt, action='deduct').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Customer list with credit balances
    customers = User.objects.filter(user_type='customer').order_by('full_name')

    # Day-by-day sales summary
    daily = orders_qs.annotate(day=TruncDate('completed_at')).values('day').annotate(total=Sum('paid_amount')).order_by('day')

    # Inventory items
    items = MenuItem.objects.all().select_related('category').order_by('category__name', 'name')

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=6)
    heading = Paragraph('POS Overview Report', title_style)
    timestamp = Paragraph(f"Generated: {timezone.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}", normal)

    story = [heading, timestamp, Spacer(1, 8)]

    # Totals table
    story.append(Paragraph('Summary Totals', styles['Heading2']))
    totals_data = [
        ['Metric', 'Amount (NPR)'],
        ['Total Sales', f'{total_sales:.2f}'],
        ['Total Credit Given', f'{credit_given:.2f}'],
        ['Total Credit Recovered', f'{credit_recovered:.2f}'],
    ]
    t = Table(totals_data, hAlign='LEFT', colWidths=[120*mm, 50*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Customer credit list
    story.append(Paragraph('Customer Credit Balances', styles['Heading2']))
    cust_table = [['Customer', 'Credit Balance (NPR)']]
    for c in customers:
        cust_table.append([c.full_name or str(c), f'{(c.credit_balance or Decimal("0.00")):.2f}'])
    ct = Table(cust_table, hAlign='LEFT', colWidths=[120*mm, 50*mm])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(ct)
    story.append(Spacer(1, 12))

    # Daily summary
    story.append(Paragraph('Day-by-day Sales Summary', styles['Heading2']))
    daily_table = [['Date', 'Sales (NPR)']]
    for d in daily:
        day_label = d['day'].strftime('%Y-%m-%d') if d.get('day') else ''
        daily_table.append([day_label, f"{(d['total'] or Decimal('0.00')):.2f}"])
    dt = Table(daily_table, hAlign='LEFT', colWidths=[120*mm, 50*mm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(dt)
    story.append(Spacer(1, 12))

    # Inventory list
    story.append(Paragraph('Inventory Snapshot', styles['Heading2']))
    inv_table = [['Item', 'Current Stock', 'Stock Value (NPR)', 'Cost Price (NPR)', 'Selling Price (NPR)']]
    for it in items:
        cost = getattr(it, 'cost_price', None)
        # If cost_price is not available, fall back to selling price for stock value calculation.
        unit_cost = cost if cost is not None else it.price
        stock_val = (unit_cost or Decimal('0.00')) * (it.stock_quantity or 0)
        inv_table.append([
            f"{it.name} ({it.category.name if it.category else ''})",
            str(it.stock_quantity or 0),
            f"{stock_val:.2f}",
            f"{(cost or Decimal('0.00')):.2f}",
            f"{(it.price or Decimal('0.00')):.2f}"
        ])
    itbl = Table(inv_table, hAlign='LEFT', colWidths=[70*mm, 25*mm, 30*mm, 30*mm, 30*mm])
    itbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(itbl)
    story.append(Spacer(1, 12))

    # Expense details removed (Expense feature deleted)

    # Footer note (cafe name + timestamp)
    story.append(PageBreak())
    story.append(Paragraph('End of Report', styles['Heading3']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('Zorpido Cafe - Generated by Zorpido POS', normal))
    story.append(Paragraph(timezone.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z'), normal))

    # Build PDF
    try:
        doc.build(story)
    except Exception as e:
        return HttpResponse(f'Failed to generate PDF: {e}', status=500)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='pos_overview_report.pdf')


@login_required
@user_passes_test(is_staff_or_admin)
def export_inventory_pdf(request):
    """Export inventory report as PDF."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import mm
    except ImportError:
        return HttpResponse('reportlab is not installed. Please pip install reportlab', status=500)

    items = MenuItem.objects.all().select_related('category').order_by('category__name', 'name')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph('Inventory Report', styles['Heading1']))
    story.append(Paragraph(f"Generated: {timezone.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}", styles['Normal']))
    story.append(Spacer(1, 8))

    table_data = [['Item', 'Current Stock', 'Cost Price (NPR)', 'Selling Price (NPR)', 'Total Stock Value (NPR)']]
    total_value = Decimal('0.00')
    for it in items:
        cost = getattr(it, 'cost_price', None) or Decimal('0.00')
        stock_qty = it.stock_quantity or 0
        stock_val = (cost * stock_qty) if cost else Decimal('0.00')
        total_value += stock_val
        table_data.append([
            f"{it.name} ({it.category.name if it.category else ''})",
            str(stock_qty),
            f"{cost:.2f}",
            f"{(it.price or Decimal('0.00')):.2f}",
            f"{stock_val:.2f}"
        ])

    tbl = Table(table_data, hAlign='LEFT', colWidths=[70*mm, 20*mm, 30*mm, 30*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8))
    story.append(Paragraph(f'Total Inventory Value (NPR): {total_value:.2f}', styles['Heading3']))

    try:
        doc.build(story)
    except Exception as e:
        return HttpResponse(f'Failed to generate PDF: {e}', status=500)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='inventory_report.pdf')


@login_required
@user_passes_test(is_staff_or_admin)
def export_sales_pdf(request):
    """Export sales report (daily grouped) as PDF."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import mm
    except ImportError:
        return HttpResponse('reportlab is not installed. Please pip install reportlab', status=500)

    # Date range parsing (optional)
    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    today = timezone.localdate()
    try:
        if from_date_str:
            from_date = timezone.datetime.fromisoformat(from_date_str).date()
        else:
            from_date = today
        if to_date_str:
            to_date = timezone.datetime.fromisoformat(to_date_str).date()
        else:
            to_date = today
    except Exception:
        return HttpResponse('Invalid date format. Use YYYY-MM-DD', status=400)

    start_dt = timezone.make_aware(timezone.datetime.combine(from_date, timezone.datetime.min.time()))
    end_dt = timezone.make_aware(timezone.datetime.combine(to_date, timezone.datetime.max.time()))

    from orders.models import Order
    orders_qs = Order.objects.filter(status='completed', completed_at__gte=start_dt, completed_at__lte=end_dt).order_by('completed_at')

    # group by day
    daily = {}
    grand_sales = Decimal('0.00')
    grand_cost = Decimal('0.00')
    grand_orders = 0

    for order in orders_qs:
        day = order.completed_at.date()
        if day not in daily:
            daily[day] = {'orders': 0, 'sales': Decimal('0.00'), 'cost': Decimal('0.00')}
        daily[day]['orders'] += 1
        daily[day]['sales'] += (order.paid_amount or Decimal('0.00'))
        # estimate cost from order items using menu_item.cost_price if present
        for it in order.items.all():
            unit_cost = getattr(it.menu_item, 'cost_price', None) or Decimal('0.00')
            line_cost = unit_cost * (it.quantity or 0)
            daily[day]['cost'] += line_cost

    # compute grand totals
    for d in sorted(daily.keys()):
        grand_orders += daily[d]['orders']
        grand_sales += daily[d]['sales']
        grand_cost += daily[d]['cost']

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph('Sales Report', styles['Heading1']), Paragraph(f"Generated: {timezone.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}", styles['Normal']), Spacer(1,8)]

    table_data = [['Date', 'Total Orders', 'Total Sales (NPR)', 'Total Cost (NPR)', 'Profit (NPR)']]
    for d in sorted(daily.keys()):
        rec = daily[d]
        profit = (rec['sales'] or Decimal('0.00')) - (rec['cost'] or Decimal('0.00'))
        table_data.append([d.strftime('%Y-%m-%d'), str(rec['orders']), f"{rec['sales']:.2f}", f"{rec['cost']:.2f}", f"{profit:.2f}"])

    # grand totals row
    grand_profit = grand_sales - grand_cost
    table_data.append(['Grand Total', str(grand_orders), f"{grand_sales:.2f}", f"{grand_cost:.2f}", f"{grand_profit:.2f}"])

    tbl = Table(table_data, hAlign='LEFT', colWidths=[40*mm, 30*mm, 35*mm, 35*mm, 35*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(tbl)

    try:
        doc.build(story)
    except Exception as e:
        return HttpResponse(f'Failed to generate PDF: {e}', status=500)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='sales_report.pdf')


@login_required
@user_passes_test(is_staff_or_admin)
def export_customer_credit_pdf(request):
    """Export customer credit and loyalty report as PDF."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import mm
    except ImportError:
        return HttpResponse('reportlab is not installed. Please pip install reportlab', status=500)

    customers = User.objects.filter(user_type='customer').order_by('full_name')
    total_outstanding = customers.aggregate(total=Sum('credit_balance'))['total'] or Decimal('0.00')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph('Customer Credit & Loyalty Report', styles['Heading1']), Paragraph(f"Generated: {timezone.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}", styles['Normal']), Spacer(1,8)]

    table_data = [['Name', 'Phone', 'Credit Balance (NPR)', 'Loyalty Points']]
    for c in customers:
        phone = getattr(c, 'phone', '') or getattr(c, 'mobile', '') or ''
        points = getattr(c, 'loyalty_points', None)
        if points is None:
            points = getattr(c, 'loyalty_points_earned', '') or ''
        table_data.append([c.full_name or str(c), phone, f"{(c.credit_balance or Decimal('0.00')):.2f}", str(points)])

    tbl = Table(table_data, hAlign='LEFT', colWidths=[60*mm, 40*mm, 40*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(tbl)
    story.append(Spacer(1,8))
    story.append(Paragraph(f'Total Outstanding Credit (NPR): {total_outstanding:.2f}', styles['Heading3']))

    try:
        doc.build(story)
    except Exception as e:
        return HttpResponse(f'Failed to generate PDF: {e}', status=500)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='customer_credit_report.pdf')


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def open_register(request):
    """Open a new cash register"""
    try:
        # Check if there's already an open register
        if Register.objects.filter(is_open=True).exists():
            return JsonResponse({
                'success': False,
                'error': 'A register is already open'
            })

        data = json.loads(request.body)
        opening_balance = Decimal(str(data.get('opening_balance', '0.00')))

        if opening_balance < 0:
            return JsonResponse({
                'success': False,
                'error': 'Opening balance cannot be negative'
            })

        # Create new register
        register = Register.objects.create(
            opened_by=request.user,
            opening_balance=opening_balance,
            is_open=True
        )

        return JsonResponse({
            'success': True,
            'register_id': register.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def close_register(request):
    """Close the currently open register"""
    try:
        register = Register.objects.filter(is_open=True).first()
        if not register:
            return JsonResponse({
                'success': False,
                'error': 'No open register found'
            })

        # Update totals one last time
        register.recalculate_totals()
        
        # Close register
        register.is_open = False
        register.closed_by = request.user
        register.closed_at = timezone.now()
        register.save()

        return JsonResponse({
            'success': True,
            'register_id': register.id,
            'closing_balance': str(register.closing_balance)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@user_passes_test(is_staff_or_admin)
def pos_dashboard(request):
    """Render POS dashboard with credit totals and customer list (Expense feature removed)"""
    total_credit = User.objects.filter(user_type='customer').aggregate(total=Sum('credit_balance'))['total'] or Decimal('0.00')
    # Expense totals removed: Expense feature has been removed

    categories = Category.objects.all()
    customers = User.objects.filter(user_type='customer').order_by('full_name')
    sellers = Seller.objects.all().order_by('name')

    active_register = Register.objects.filter(is_open=True).first()

    context = {
        'categories': categories,
        'customers': customers,
        'sellers': sellers,
        'active_register': active_register,
        'total_credit': total_credit,
        # total_expenses removed: Expense feature removed
    }
    return render(request, 'pos/dashboard.html', context)


# Expense Category CRUD (manager/admin only)
@login_required
@user_passes_test(is_manager_or_admin)
def expense_category_list(request):
    cats = ExpenseCategory.objects.all().order_by('name')
    return render(request, 'pos/expenses/categories_list.html', {'categories': cats})


@login_required
@user_passes_test(is_manager_or_admin)
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created')
            return redirect('pos:expense_category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'pos/expenses/category_form.html', {'form': form})


@login_required
@user_passes_test(is_manager_or_admin)
def expense_category_edit(request, cat_id):
    cat = get_object_or_404(ExpenseCategory, id=cat_id)
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated')
            return redirect('pos:expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=cat)
    return render(request, 'pos/expenses/category_form.html', {'form': form, 'category': cat})


@login_required
@user_passes_test(is_manager_or_admin)
def expense_category_delete(request, cat_id):
    cat = get_object_or_404(ExpenseCategory, id=cat_id)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted')
        return redirect('pos:expense_category_list')
    return render(request, 'pos/expenses/category_form.html', {'category': cat, 'confirm_delete': True})


# Expenses CRUD (staff/admin)
@login_required
@user_passes_test(is_staff_or_admin)
def expense_list(request):
    qs = Expense.objects.select_related('category', 'created_by').all()
    # filters
    cat = request.GET.get('category')
    if cat:
        qs = qs.filter(category_id=cat)
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    if from_date:
        qs = qs.filter(date__gte=from_date)
    if to_date:
        qs = qs.filter(date__lte=to_date)

    # pagination
    from django.core.paginator import Paginator
    p = Paginator(qs.order_by('-date', '-created_at'), 25)
    page = request.GET.get('page')
    page_obj = p.get_page(page)

    categories = ExpenseCategory.objects.all()
    return render(request, 'pos/expenses/list.html', {'expenses': page_obj, 'categories': categories, 'filter_cat': cat, 'from_date': from_date, 'to_date': to_date})


@login_required
@user_passes_test(is_staff_or_admin)
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            e = form.save(commit=False)
            e.created_by = request.user
            e.save()
            messages.success(request, 'Expense recorded')
            return redirect('pos:expenses_list')
    else:
        form = ExpenseForm()
    return render(request, 'pos/expenses/form.html', {'form': form})


@login_required
@user_passes_test(is_staff_or_admin)
def expense_edit(request, expense_id):
    e = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated')
            return redirect('pos:expenses_list')
    else:
        form = ExpenseForm(instance=e)
    return render(request, 'pos/expenses/form.html', {'form': form, 'expense': e})


@login_required
@user_passes_test(is_staff_or_admin)
def expense_delete(request, expense_id):
    e = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        e.delete()
        messages.success(request, 'Expense deleted')
        return redirect('pos:expenses_list')
    return render(request, 'pos/expenses/form.html', {'expense': e, 'confirm_delete': True})


@login_required
@user_passes_test(is_staff_or_admin)
def expenses_by_category(request):
    # Aggregate totals per category for a date range
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    qs = Expense.objects.all()
    if from_date:
        qs = qs.filter(date__gte=from_date)
    if to_date:
        qs = qs.filter(date__lte=to_date)

    totals = qs.values('category__id', 'category__name').annotate(total=Sum('amount')).order_by('-total')
    # quick totals for today/week/month
    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    totals_summary = {
        'today': Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'this_week': Expense.objects.filter(date__gte=week_start, date__lte=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'this_month': Expense.objects.filter(date__gte=month_start, date__lte=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    return render(request, 'pos/expenses/categories_list.html', {'totals': totals, 'summary': totals_summary})


# REMOVED: expenses_by_category view (Expense feature removed)

@login_required
@user_passes_test(is_staff_or_admin)
def advanced_overview(request):
    """Render the Advanced Overview analytics page (UI). Data is fetched via the API endpoint."""
    return render(request, 'pos/advanced_overview.html', {})


@login_required
@user_passes_test(is_staff_or_admin)
def api_overview_data(request):
    """Return JSON summary and time-series data for the advanced overview.

    Query param: range=day|week|month (defaults to 'week')
    """
    rng = request.GET.get('range', 'week')
    today = timezone.localdate()

    if rng == 'day':
        days = 1
    elif rng == 'month':
        days = 30
    else:
        days = 7

    start_date = today - timezone.timedelta(days=days - 1)
    start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
    end_dt = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    # Sales and orders
    orders_qs = Order.objects.filter(status='completed', completed_at__gte=start_dt, completed_at__lte=end_dt)
    sales_total = orders_qs.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')

    # Expense feature removed: no expense totals available
    expenses_total = Decimal('0.00')

    # Receivables (customer credit balances)
    receivables = User.objects.filter(user_type='customer').aggregate(total=Sum('credit_balance'))['total'] or Decimal('0.00')

    # Payables - try common purchase models, fallback to zero
    # Outstanding payables from Payable model
    try:
        payables_total = Payable.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    except Exception:
        payables_total = Decimal('0.00')

    # Active customers (customers with at least one completed order in range)
    active_customers = User.objects.filter(user_type='customer', orders__status='completed', orders__completed_at__gte=start_dt, orders__completed_at__lte=end_dt).distinct().count()

    # Inventory value
    inventory_value = Decimal('0.00')
    for it in MenuItem.objects.all().only('stock_quantity', 'price'):
        stock = it.stock_quantity or 0
        cost = getattr(it, 'cost_price', None) or it.price or Decimal('0.00')
        try:
            inventory_value += (Decimal(str(cost)) * Decimal(stock))
        except Exception:
            pass

    # Build daily series for chart
    labels = []
    sales_data = []
    cur = start_date
    while cur <= today:
        labels.append(cur.strftime('%Y-%m-%d'))
        day_start = timezone.make_aware(timezone.datetime.combine(cur, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(cur, timezone.datetime.max.time()))
        day_sales = Order.objects.filter(status='completed', completed_at__gte=day_start, completed_at__lte=day_end).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')
        sales_data.append(float(day_sales))
        cur = cur + timezone.timedelta(days=1)

    summary = {
        'total_sales': float(sales_total),
        'net_profit': float(sales_total or Decimal('0.00')),  # no expenses to subtract
        'total_payables': float(payables_total),
        'total_receivables': float(receivables),
        'active_customers': active_customers,
        'inventory_value': float(inventory_value),
    }

    data = {
        'summary': summary,
        'series': {
            'labels': labels,
            'sales': sales_data,
        }
    }

    return JsonResponse(data)


@login_required
def inventory_management(request):

    if not is_staff_or_admin(request.user) and not request.user.has_perm('menu.manage_inventory'):
        from django.contrib import messages
        messages.error(request, 'You do not have permission to view inventory management')
        return redirect('pos:dashboard')

    low_stock_qs = MenuItem.objects.filter(stock_quantity__lte=F('low_stock_threshold')).select_related('category').order_by('stock_quantity')
    all_qs = MenuItem.objects.all().select_related('category').order_by('category__name', 'name')

    # Prepare simple serializable lists with computed margin (selling - purchase)
    def annotate_list(qs):
        out = []
        for item in qs:
            purchase = getattr(item, 'purchase_price', None) or Decimal('0.00')
            try:
                margin = (item.price or Decimal('0.00')) - purchase
            except Exception:
                margin = Decimal('0.00')
            out.append({
                'id': item.id,
                'name': item.name,
                'category': getattr(item.category, 'name', ''),
                'stock_quantity': item.stock_quantity,
                'low_stock_threshold': item.low_stock_threshold,
                'availability': item.availability,
                'price': item.price,
                'purchase_price': purchase,
                'margin': margin,
                'is_low_stock': item.is_low_stock if hasattr(item, 'is_low_stock') else (item.stock_quantity <= (item.low_stock_threshold or 0))
            })
        return out

    low_stock_items = annotate_list(low_stock_qs)
    all_items = annotate_list(all_qs)
    return render(request, 'pos/inventory.html', {'low_stock_items': low_stock_items, 'all_items': all_items})


@require_POST
def update_stock(request, item_id):
    # Auth checks (return JSON for AJAX)
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    if not (is_staff_or_admin(request.user) or request.user.has_perm('menu.manage_inventory')):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    # Require an open register for inventory adjustments
    reg_err = _require_open_register_json()
    if reg_err:
        return reg_err

    try:
        item = get_object_or_404(MenuItem, id=item_id)
        data = json.loads(request.body)
        
        # Validate action
        action = (data.get('action') or '').lower()
        if action not in ('add', 'set', 'decrease'):
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

        # Validate quantity
        try:
            quantity = int(data.get('quantity', 0))
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Quantity must be an integer'}, status=400)
        if quantity < 0:
            return JsonResponse({'success': False, 'error': 'Quantity must be non-negative'}, status=400)

        # Update stock
        if action == 'add':
            if quantity <= 0:
                return JsonResponse({'success': False, 'error': 'Quantity to add must be greater than zero'}, status=400)
            if hasattr(item, 'increase_stock'):
                item.increase_stock(quantity)
            else:
                item.stock_quantity = (item.stock_quantity or 0) + quantity
                item.save()
        elif action == 'decrease':
            if quantity <= 0:
                return JsonResponse({'success': False, 'error': 'Quantity to decrease must be greater than zero'}, status=400)
            current = item.stock_quantity or 0
            if quantity > current:
                return JsonResponse({'success': False, 'error': 'Cannot decrease more than current stock'}, status=400)
            # Prefer model method if available
            if hasattr(item, 'reduce_stock'):
                ok = item.reduce_stock(quantity)
                if not ok:
                    return JsonResponse({'success': False, 'error': 'Insufficient stock to decrease'}, status=400)
            else:
                item.stock_quantity = current - quantity
                if item.stock_quantity <= 0:
                    item.stock_quantity = 0
                    item.availability = 'out_of_stock'
                item.save()
        else:  # action == 'set'
            item.stock_quantity = quantity
            if quantity > 0 and getattr(item, 'availability', None) == 'out_of_stock':
                item.availability = 'available'
            item.save()

        # Update optional settings
        low_threshold = data.get('low_threshold')
        if low_threshold is not None:
            try:
                item.low_stock_threshold = int(low_threshold)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Low threshold must be an integer'}, status=400)

        availability = data.get('availability')
        if availability:
            # Build valid keys from the AVAILABILITY_CHOICES tuple
            valid = [k for k, _ in getattr(MenuItem, 'AVAILABILITY_CHOICES', [])]
            if availability in valid:
                item.availability = availability
            else:
                return JsonResponse({'success': False, 'error': 'Invalid availability value'}, status=400)

        # Update optional settings
        low_threshold = data.get('low_threshold')
        if low_threshold is not None:
            try:
                item.low_stock_threshold = int(low_threshold)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Low threshold must be an integer'}, status=400)

        availability = data.get('availability')
        if availability:
            # Build valid keys from the AVAILABILITY_CHOICES tuple
            valid = [k for k, _ in getattr(MenuItem, 'AVAILABILITY_CHOICES', [])]
            if availability in valid:
                item.availability = availability
            else:
                return JsonResponse({'success': False, 'error': 'Invalid availability value'}, status=400)

        # Ensure final save
        # Accept price and purchase_price updates (selling and cost)
        try:
            if 'purchase_price' in data:
                from decimal import Decimal, InvalidOperation
                try:
                    item.purchase_price = Decimal(str(data.get('purchase_price') or '0'))
                except (InvalidOperation, ValueError):
                    return JsonResponse({'success': False, 'error': 'Invalid purchase_price value'}, status=400)
            if 'price' in data:
                from decimal import Decimal, InvalidOperation
                try:
                    item.price = Decimal(str(data.get('price') or '0'))
                except (InvalidOperation, ValueError):
                    return JsonResponse({'success': False, 'error': 'Invalid price value'}, status=400)
        except Exception:
            pass

        item.save()
        return JsonResponse({'success': True, 'new_stock': item.stock_quantity, 'availability': item.availability, 'availability_display': item.get_availability_display()})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def customer_credit_management(request):
    """Render customer credit management page"""
    customers = User.objects.filter(user_type='customer').order_by('full_name')
    total_credit = customers.aggregate(total=Sum('credit_balance'))['total'] or Decimal('0.00')
    return render(request, 'pos/credit_management.html', {'customers': customers, 'total_credit': total_credit})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def update_customer_credit(request, customer_id):
    """Add or deduct customer credit balance"""
    try:
        customer = get_object_or_404(User, id=customer_id, user_type='customer')
        data = json.loads(request.body)
        action = data.get('action')

        # Validate amount
        try:
            amount = Decimal(str(data.get('amount', '0')))
        except InvalidOperation:
            return JsonResponse({'success': False, 'error': 'Invalid amount'})
        if amount <= Decimal('0'):
            return JsonResponse({'success': False, 'error': 'Amount must be positive'})

        # Require open register for credit adjustments
        reg_err = _require_open_register_json()
        if reg_err:
            return reg_err

        # Process credit update
        if action == 'add':
            customer.add_credit(amount)
            note = 'Manual adjustment'
        elif action == 'deduct':
            if not customer.deduct_credit(amount):
                return JsonResponse({'success': False, 'error': 'Insufficient balance'})
            note = 'Manual deduction'
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})

        # Record transaction
        CreditTransaction.objects.create(
            user=customer,
            amount=amount,
            action=action,
            balance_after=customer.credit_balance,
            note=note,
            staff=request.user
        )
        
        return JsonResponse({'success': True, 'new_balance': str(customer.credit_balance)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def credit_history(request, customer_id):
    """Get customer credit transaction history"""
    try:
        customer = get_object_or_404(User, id=customer_id, user_type='customer')
        
        # Query transactions with date filtering
        qs = CreditTransaction.objects.filter(user=customer).order_by('-created_at')
        from_date = request.GET.get('from')
        to_date = request.GET.get('to')
        
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)

        # Format transaction data
        transactions = [{
            'id': t.id,
            'amount': str(t.amount),
            'action': t.action,
            'action_display': t.get_action_display(),
            'balance_after': str(t.balance_after),
            'note': t.note,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for t in qs[:200]]

        return JsonResponse({'success': True, 'transactions': transactions})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def seller_list(request):
    sellers = Seller.objects.all().order_by('name')
    return render(request, 'pos/sellers/list.html', {'sellers': sellers})


@login_required
@user_passes_test(is_staff_or_admin)
def seller_detail(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    payables = seller.payables.order_by('status', 'created_at')
    purchases = []
    total_payable = seller.total_payable()
    total_paid = seller.total_paid()
    return render(request, 'pos/sellers/detail.html', {
        'seller': seller,
        'payables': payables,
        'purchases': purchases,
        'total_payable': total_payable,
        'total_paid': total_paid
    })


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def pay_seller_payable(request, seller_id):
    """Handle payment towards a seller's outstanding payables.

    Expects JSON body: { amount: '123.45', payment_mode: 'cash'|'qr', remark: 'optional' }
    """
    try:
        seller = get_object_or_404(Seller, id=seller_id)
        # Support both JSON and form-encoded POSTs
        payment_mode = 'cash'
        remark = ''
        payable_id = None
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            try:
                amount = Decimal(str(data.get('amount', '0')))
            except Exception:
                return JsonResponse({'success': False, 'error': 'Invalid amount'}, status=400)
            payment_mode = data.get('payment_mode') or 'cash'
            remark = data.get('remark') or ''
            payable_id = data.get('payable_id')
        else:
            # form POST
            try:
                amount = Decimal(str(request.POST.get('amount_paid') or request.POST.get('amount') or '0'))
            except Exception:
                return JsonResponse({'success': False, 'error': 'Invalid amount'}, status=400)
            payment_mode = request.POST.get('payment_mode') or request.POST.get('payment_mode') or 'cash'
            remark = request.POST.get('remark') or ''
            payable_id = request.POST.get('payable_id') or None

        if amount <= Decimal('0.00'):
            return JsonResponse({'success': False, 'error': 'Amount must be greater than zero'}, status=400)

        # Check total payable
        total_payable = seller.total_payable() or Decimal('0.00')
        if amount > total_payable:
            return JsonResponse({'success': False, 'error': 'Amount exceeds total payable'}, status=400)

        applied = Decimal('0.00')
        last_remaining = None
        last_settled = None

        with transaction.atomic():
            # If a specific payable_id provided, apply only to that payable
            if payable_id:
                try:
                    p = seller.payables.select_for_update().get(id=int(payable_id), status='pending')
                except Exception:
                    return JsonResponse({'success': False, 'error': 'Selected payable not found or already settled'}, status=404)

                apply_amt = min(p.remaining_amount or Decimal('0.00'), amount)
                if apply_amt <= Decimal('0.00'):
                    return JsonResponse({'success': False, 'error': 'Nothing to apply'}, status=400)

                p.remaining_amount = (p.remaining_amount or Decimal('0.00')) - apply_amt
                if p.remaining_amount <= Decimal('0.00'):
                    p.remaining_amount = Decimal('0.00')
                    p.status = 'settled'
                    p.paid_at = timezone.now()
                p.save()

                # related_expense handling removed (Expense model deleted)

                # Record payment history
                from .models import PayablePaymentHistory
                PayablePaymentHistory.objects.create(
                    seller=seller,
                    payable=p,
                    amount=apply_amt,
                    payment_mode=payment_mode,
                    remark=remark,
                    staff=request.user
                )

                applied = apply_amt
                last_remaining = p.remaining_amount
                last_settled = (p.status == 'settled')

            else:
                # No specific payable selected: apply FIFO across payables
                remaining = amount
                pending_qs = seller.payables.filter(status='pending').order_by('created_at').select_for_update()
                for p in pending_qs:
                    if remaining <= Decimal('0.00'):
                        break
                    apply_amt = min(p.remaining_amount or Decimal('0.00'), remaining)
                    if apply_amt <= Decimal('0.00'):
                        continue
                    p.remaining_amount = (p.remaining_amount or Decimal('0.00')) - apply_amt
                    if p.remaining_amount <= Decimal('0.00'):
                        p.remaining_amount = Decimal('0.00')
                        p.status = 'settled'
                        p.paid_at = timezone.now()
                    p.save()

                    # related_expense handling removed (Expense model deleted)

                    from .models import PayablePaymentHistory
                    PayablePaymentHistory.objects.create(
                        seller=seller,
                        payable=p,
                        amount=apply_amt,
                        payment_mode=payment_mode,
                        remark=remark,
                        staff=request.user
                    )

                    remaining -= apply_amt
                    applied += apply_amt
                    last_remaining = p.remaining_amount
                    last_settled = (p.status == 'settled')

            # Update open register totals if payment was cash/qr
            try:
                open_reg = Register.objects.filter(is_open=True).order_by('-opened_at').first()
                if open_reg and applied > Decimal('0.00'):
                    if payment_mode == 'cash':
                        open_reg.cash_total = (open_reg.cash_total or Decimal('0.00')) + applied
                    elif payment_mode == 'qr':
                        open_reg.qr_total = (open_reg.qr_total or Decimal('0.00')) + applied
                    open_reg.recalculate_totals()
            except Exception:
                logging.exception('Failed to update register after payable settlement')

        resp = {'success': True, 'applied': str(applied), 'total_payable': str(seller.total_payable()), 'total_paid': str(seller.total_paid())}
        if last_remaining is not None:
            # return numeric remaining amount and settled flag
            try:
                resp['remaining_amount'] = float(last_remaining)
            except Exception:
                resp['remaining_amount'] = float(str(last_remaining))
            resp['settled'] = bool(last_settled)
        return JsonResponse(resp)
    except Exception as e:
        logging.exception('Error in pay_seller_payable')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def seller_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        notes = request.POST.get('notes')
        if not name:
            messages.error(request, 'Name is required')
            return redirect('pos:seller_list')
        Seller.objects.create(name=name, contact=contact or '', email=email or '', notes=notes or '')
        messages.success(request, 'Seller created')
        return redirect('pos:seller_list')
    return render(request, 'pos/sellers/create.html')


@login_required
@user_passes_test(is_staff_or_admin)
def seller_delete(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    if request.method == 'POST':
        seller.delete()
        messages.success(request, 'Seller deleted')
        return redirect('pos:seller_list')
    return render(request, 'pos/sellers/confirm_delete.html', {'seller': seller})


def _generate_payment_qr_image(order):
    """Generate QR code for payment"""
    if not qrcode:
        return None
        
    payment_data = (
        f"Zorpido Order: {order.order_number}\n"
        f"Amount: NPR {order.total}\n"
        "Pay at counter or scan to pay"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payment_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    return base64.b64encode(buffer.getvalue()).decode()


@login_required
@user_passes_test(is_staff_or_admin)
def payment_screen(request, order_id):
    """Show payment screen for an order"""
    from orders.models import Order
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'completed':
        return redirect('pos:completed_orders')
        
    qr_code_data = None
    if request.GET.get('payment_method') == 'qr':
        qr_code_data = _generate_payment_qr_image(order)
        
    return render(request, 'pos/payment.html', {
        'order': order,
        'qr_code_data': qr_code_data
    })


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def complete_payment(request, order_id):
    """Complete order payment and update register"""
    from orders.models import Order
    try:
        order = get_object_or_404(Order, id=order_id)
        data = json.loads(request.body)
        payment_method = data.get('payment_method')

        # Validate payment method
        if payment_method not in ['cash', 'qr', 'credit']:
            return JsonResponse({'success': False, 'error': 'Invalid payment method'})

        # Handle credit payment
        # Note: credit-mode for orders means the customer is placed on credit (deferred payment).
        # The order completion should not require a pre-existing balance. Order.mark_as_completed()
        # will create the owed credit transaction and update the customer's balance.
        if payment_method == 'credit':
            if not order.customer:
                return JsonResponse({
                    'success': False,
                    'error': 'Customer required for credit payment'
                })

        # Require open register before completing payment
        reg_err = _require_open_register_json()
        if reg_err:
            return reg_err

        # Complete order
        order.payment_method = payment_method
        order.paid_amount = order.total
        order.mark_as_completed()

        # Update register totals
        try:
            open_reg = Register.objects.filter(
                is_open=True
            ).order_by('-opened_at').first()
            
            if open_reg:
                if payment_method == 'cash':
                    open_reg.cash_total = (
                        open_reg.cash_total or Decimal('0.00')
                    ) + order.paid_amount
                elif payment_method == 'credit':
                    open_reg.credit_total = (
                        open_reg.credit_total or Decimal('0.00')
                    ) + order.paid_amount
                elif payment_method == 'qr':
                    open_reg.qr_total = (
                        open_reg.qr_total or Decimal('0.00')
                    ) + order.paid_amount
                open_reg.save()
        except Exception:
            # Non-critical if register update fails
            pass

        return JsonResponse({
            'success': True,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
def completed_orders(request):
    """Show list of completed orders"""
    orders = Order.objects.filter(
        status='completed'
    ).order_by('-completed_at')[:50]
    return render(request, 'pos/completed_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_staff_or_admin)
def register_detail(request, reg_id):
    """Show full details for a register: orders, expenses, credit transactions within register timeframe."""
    register = get_object_or_404(Register, id=reg_id)

    start = register.opened_at
    end = register.closed_at or timezone.now()

    # Orders completed within register timeframe
    orders = Order.objects.filter(status='completed', completed_at__gte=start, completed_at__lte=end).order_by('-completed_at')

    # Expenses within register timeframe (by date)
    try:
        expenses = Expense.objects.filter(date__gte=start.date(), date__lte=end.date()).order_by('-created_at')
    except Exception:
        expenses = []

    # Credit transactions within timeframe
    credits = CreditTransaction.objects.filter(created_at__gte=start, created_at__lte=end).order_by('-created_at')

    context = {
        'register': register,
        'orders': orders,
        'expenses': expenses,
        'credits': credits,
        'start': start,
        'end': end,
    }
    return render(request, 'pos/register_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def created_orders(request):
    """Show list of pending orders"""
    orders = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready']
    ).select_related(
        'customer', 
        'staff'
    ).prefetch_related(
        'items'
    ).order_by('-created_at')
    return render(request, 'pos/created_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def complete_order(request, order_id):
    """Mark an order as completed"""
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Order already completed'
            })
        order.mark_as_completed()
        return JsonResponse({
            'success': True,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def delete_order(request, order_id):
    """Delete a pending order"""
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete completed order'
            })
        order.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def add_item_to_order(request, order_id):
    """Add an item to an order"""
    try:
        # Require open register
        reg_err = _require_open_register_json()
        if reg_err:
            return reg_err

        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False, 
                'error': 'Cannot modify completed order'
            })
            
        data = json.loads(request.body)
        menu_item = get_object_or_404(MenuItem, id=data['item_id'])
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Quantity must be positive'
            })

        # Update or create order item
        existing_item = OrderItem.objects.filter(
            order=order,
            menu_item=menu_item
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )

        # Reduce stock
        if hasattr(menu_item, 'reduce_stock'):
            menu_item.reduce_stock(quantity)
        else:
            menu_item.stock_quantity = (menu_item.stock_quantity or 0) - quantity
            menu_item.save()

        # Update order total
        order.calculate_totals()
        
        return JsonResponse({
            'success': True,
            'total': str(order.total)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def remove_item_from_order(request, order_id, item_id):
    """Remove an item from an order"""
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Cannot modify completed order'
            })

        item = get_object_or_404(OrderItem, id=item_id, order=order)

        # Return stock
        if hasattr(item.menu_item, 'increase_stock'):
            item.menu_item.increase_stock(item.quantity)
        else:
            item.menu_item.stock_quantity = (
                item.menu_item.stock_quantity or 0
            ) + item.quantity
            item.menu_item.save()

        # Remove item and update total
        item.delete()
        order.calculate_totals()

        return JsonResponse({
            'success': True,
            'total': str(order.total)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

        # Complete order
        order.payment_method = payment_method
        order.paid_amount = order.total
        order.mark_as_completed()

        # Update register totals
        try:
            open_reg = Register.objects.filter(
                is_open=True
            ).order_by('-opened_at').first()
            
            if open_reg:
                if payment_method == 'cash':
                    open_reg.cash_total = (
                        open_reg.cash_total or Decimal('0.00')
                    ) + order.paid_amount
                elif payment_method == 'credit':
                    open_reg.credit_total = (
                        open_reg.credit_total or Decimal('0.00')
                    ) + order.paid_amount
                elif payment_method == 'qr':
                    open_reg.qr_total = (
                        open_reg.qr_total or Decimal('0.00')
                    ) + order.paid_amount
                open_reg.save()
        except Exception:
            # Non-critical if register update fails
            pass

        return JsonResponse({
            'success': True,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
def completed_orders(request):
    """Show list of completed orders"""
    from orders.models import Order
    orders = Order.objects.filter(
        status='completed'
    ).order_by('-completed_at')[:50]
    return render(request, 'pos/completed_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_staff_or_admin)
def created_orders(request):
    """Show list of pending orders"""
    from orders.models import Order
    orders = Order.objects.exclude(
        status='completed'
    ).order_by('-created_at')
    return render(request, 'pos/created_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def complete_order(request, order_id):
    """Mark an order as completed"""
    from orders.models import Order
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Order already completed'
            })
        order.mark_as_completed()
        return JsonResponse({
            'success': True,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def delete_order(request, order_id):
    """Delete a pending order"""
    from orders.models import Order
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete completed order'
            })
        order.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




