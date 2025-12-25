from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.http import FileResponse, HttpResponse, JsonResponse
from io import BytesIO
from decimal import Decimal
from .forms import (
    CustomerRegistrationForm, CustomLoginForm, ProfileUpdateForm, 
    StaffLoginForm, CustomPasswordResetForm, ResetPasswordForm
)
from .models import User
from .utils import send_password_reset_email, verify_token
from .forms import StaffCustomerForm, CreditAdjustmentForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction


def customer_register(request):
	"""Handle customer registration: display form and create user."""
	if request.method == 'POST':
		form = CustomerRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=True, request=request)
			messages.success(
				request,
				'Registration successful! You can now log in using your email and password.'
			)
			return redirect('users:login')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = CustomerRegistrationForm()

	return render(request, 'users/register.html', {'form': form})


def customer_login(request):
	"""Authenticate and log in a user using the custom login form."""
	if request.method == 'POST':
		form = CustomLoginForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			messages.success(request, f'Welcome back, {user.get_short_name() or user.email}!')
			return redirect('website:home')
		else:
			messages.error(request, 'Invalid email or password.')
	else:
		form = CustomLoginForm(request)

	return render(request, 'users/login.html', {'form': form})


def staff_login(request):
	"""Authenticate and log in a staff user only.

	On success redirect to POS dashboard (`pos:dashboard`).
	"""
	# Support optional next parameter to redirect after login
	next_url = request.GET.get('next') or request.POST.get('next')

	if request.method == 'POST':
		form = StaffLoginForm(request, data=request.POST)
		# Extract raw credentials to try explicit authenticate (so we can distinguish reasons)
		username_input = request.POST.get('username')
		password_input = request.POST.get('password')

		auth_user = None
		if username_input and password_input:
			# First try direct username authentication
			auth_user = authenticate(request, username=username_input, password=password_input)

			# If not found, try treating the username input as email (case-insensitive)
			if auth_user is None:
				try:
					possible = User.objects.filter(email__iexact=username_input).first()
					if possible:
						auth_user = authenticate(request, username=possible.username, password=password_input)
				except Exception:
					auth_user = None

		# If authentication succeeded, check staff status and active flag
		if auth_user is not None:
			if not auth_user.is_active:
				messages.error(request, 'This staff account is inactive. Contact admin.')
			elif getattr(auth_user, 'user_type', None) != 'staff':
				messages.error(request, 'Your account is not a staff account. Use customer login or request staff access.')
			else:
				# All good: log in
				login(request, auth_user)
				messages.success(request, f'Welcome, {auth_user.get_short_name() or auth_user.username}!')
				if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
					return redirect(next_url)
				return redirect('pos:dashboard')

		# If we reach here, either credentials invalid or form not valid
		# Prefer showing invalid credentials over form errors so staff get clear feedback
		messages.error(request, 'Invalid staff credentials. Please check username/email and password.')
	else:
		form = StaffLoginForm(request)

	return render(request, 'users/staff_login.html', {'form': form, 'next': next_url})


def customer_logout(request):
	logout(request)
	messages.info(request, 'You have been logged out.')
	return redirect('website:home')


@staff_member_required
def staff_customer_list(request):
	"""List all customers for staff management"""
	customers = User.objects.filter(user_type='customer')
	return render(request, 'users/staff/customer_list.html', {'customers': customers})


@staff_member_required
def staff_customer_edit(request, pk):
	"""Edit a customer profile (including credit and loyalty)"""
	customer = get_object_or_404(User, pk=pk, user_type='customer')
	if request.method == 'POST':
		form = StaffCustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Customer updated successfully.')
				return redirect('users:staff_customer_list')
			except Exception as e:
				try:
					form.add_error('profile_upload', str(e))
				except Exception:
					pass
				messages.error(request, f'Customer update failed: {e}')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = StaffCustomerForm(instance=customer)
	# Consolidate credit transactions from POS and loyalty
	credit_history = []
	try:
		from pos.models import CreditTransaction as PosCreditTransaction
		pos_txns = PosCreditTransaction.objects.filter(user=customer).values('id', 'amount', 'action', 'balance_after', 'note', 'staff', 'created_at')
		for t in pos_txns:
			credit_history.append({
				'source': 'pos',
				'id': t['id'],
				'amount': t['amount'],
				'type': t['action'],
				'note': t['note'],
				'staff': t['staff'],
				'created_at': t['created_at'],
			})
	except Exception:
		pass

	try:
		from loyalty.models import CreditTransaction as LoyaltyCreditTransaction
		loyalty_txns = LoyaltyCreditTransaction.objects.filter(customer=customer).values('id', 'amount', 'transaction_type', 'description', 'created_at')
		for t in loyalty_txns:
			credit_history.append({
				'source': 'loyalty',
				'id': t['id'],
				'amount': t['amount'],
				'type': t['transaction_type'],
				'note': t['description'],
				'created_at': t['created_at'],
			})
	except Exception:
		pass

	# Sort by created_at descending
	credit_history.sort(key=lambda x: x.get('created_at') or 0, reverse=True)

	return render(request, 'users/staff/customer_edit.html', {'form': form, 'customer': customer, 'credit_history': credit_history})


@staff_member_required
@transaction.atomic
def staff_adjust_credit(request, pk):
	customer = get_object_or_404(User, pk=pk, user_type='customer')
	if request.method == 'POST':
		form = CreditAdjustmentForm(request.POST)
		if form.is_valid():
			action = form.cleaned_data['action']
			amount = form.cleaned_data['amount']
			note = form.cleaned_data['note']

			from loyalty.models import CreditTransaction

			if action == 'add':
				customer.add_credit(amount)
				txn_type = 'credit_added'
			else:
				# deduct or adjust
				# Ensure sufficient balance for deduct
				if action == 'deduct' and customer.credit_balance < amount:
					messages.error(request, 'Insufficient credit balance for deduction.')
					return redirect('users:staff_customer_edit', pk=pk)
				# Deduct
				customer.deduct_credit(amount)
				txn_type = 'credit_deducted' if action == 'deduct' else 'adjustment'

			# Log transaction
			CreditTransaction.objects.create(
				customer=customer,
				transaction_type=txn_type,
				amount=amount,
				description=note,
			)

			messages.success(request, 'Credit updated and transaction logged.')
			return redirect('users:staff_customer_edit', pk=pk)
	else:
		form = CreditAdjustmentForm()
	return render(request, 'users/staff/adjust_credit.html', {'form': form, 'customer': customer})


@login_required
def customer_profile(request):
	"""Allow customers to view and update their profile details."""
	if request.method == 'POST':
		form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			# Save the form (handles uploaded files). Wrap upload errors
			# so we can show them inline instead of erroring the request.
			try:
				form.save()
				request.user.refresh_from_db()
				messages.success(request, 'Profile updated successfully.')
				return redirect('users:dashboard')
			except Exception as e:
				# Attach error to the profile_upload field if possible and re-render form
				try:
					form.add_error('profile_upload', str(e))
				except Exception:
					pass
				messages.error(request, f'Profile update failed: {e}')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = ProfileUpdateForm(instance=request.user)

	return render(request, 'users/profile.html', {'form': form})


@login_required
def customer_dashboard(request):
	# Gather data: credit balance, recent credit transactions, loyalty history
	credit_balance = request.user.credit_balance
	loyalty_points = request.user.loyalty_points
	recent_credits = request.user.credit_transactions.all()[:10]
	recent_loyalty = request.user.loyalty_transactions.all()[:10]  # Ensure loyalty history is passed
	return render(request, 'users/dashboard.html', {
		'credit_balance': credit_balance,
		'loyalty_points': loyalty_points,
		'recent_credits': recent_credits,
		'recent_loyalty': recent_loyalty,  # Include loyalty transactions in context
	})


@login_required
def export_my_profile_pdf(request):
	"""Generate a PDF for the logged-in customer's profile (personal info + full credit & loyalty history)."""
	try:
		from reportlab.lib.pagesizes import A4
		from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
		from reportlab.lib.styles import getSampleStyleSheet
		from reportlab.lib import colors
		from reportlab.lib.units import mm
	except ImportError:
		return HttpResponse('reportlab is not installed. Please pip install reportlab', status=500)

	user = request.user

	# Gather credit history (POS + loyalty) for this user
	credit_history = []
	try:
		from pos.models import CreditTransaction as PosCreditTransaction
		pos_txns = PosCreditTransaction.objects.filter(user=user).order_by('-created_at')
		for t in pos_txns:
			credit_history.append({
				'date': t.created_at,
				'amount': t.amount,
				'type': t.action,
				'note': getattr(t, 'note', '')
			})
	except Exception:
		pass

	try:
		from loyalty.models import CreditTransaction as LoyaltyCreditTransaction
		loy_txns = LoyaltyCreditTransaction.objects.filter(customer=user).order_by('-created_at')
		for t in loy_txns:
			credit_history.append({
				'date': t.created_at,
				'amount': getattr(t, 'amount', None) or getattr(t, 'value', None) or Decimal('0.00'),
				'type': getattr(t, 'transaction_type', 'loyalty'),
				'note': getattr(t, 'description', '')
			})
	except Exception:
		pass

	# Loyalty transactions (points)
	loyalty_history = []
	try:
		from loyalty.models import LoyaltyTransaction
		loy = LoyaltyTransaction.objects.filter(customer=user).order_by('-created_at')
		for t in loy:
			loyalty_history.append({
				'date': t.created_at,
				'points': getattr(t, 'points', 0),
				'type': getattr(t, 'transaction_type', ''),
				'note': getattr(t, 'description', '')
			})
	except Exception:
		# If LoyaltyTransaction not available, attempt to use fields on user model
		pass

	# Build PDF
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
	styles = getSampleStyleSheet()
	normal = styles['Normal']
	story = []

	story.append(Paragraph('My Profile Report', styles['Heading1']))
	story.append(Paragraph(f'Generated: {timezone.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")}', normal))
	story.append(Spacer(1, 8))

	# Personal details
	story.append(Paragraph('Personal Details', styles['Heading2']))
	details_table = [
		['Full Name', user.full_name or ''],
		['Email', user.email or ''],
		['Phone', user.phone or ''],
		['Address / Location', user.location or ''],
	]
	t = Table(details_table, hAlign='LEFT', colWidths=[50*mm, 110*mm])
	t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.grey)]))
	story.append(t)
	story.append(Spacer(1, 12))

	# Credit history
	story.append(Paragraph('Credit Transaction History', styles['Heading2']))
	ch_data = [['Date', 'Type', 'Amount (NPR)', 'Note']]
	for c in sorted(credit_history, key=lambda x: x.get('date') or timezone.now(), reverse=True):
		ch_data.append([c.get('date').strftime('%Y-%m-%d %H:%M') if c.get('date') else '', c.get('type', ''), f"{(c.get('amount') or Decimal('0.00')):.2f}", c.get('note', '')[:80]])
	if len(ch_data) == 1:
		ch_data.append(['-', '-', '-', 'No transactions'])
	ch_tbl = Table(ch_data, hAlign='LEFT', colWidths=[35*mm, 40*mm, 35*mm, 70*mm])
	ch_tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')), ('GRID', (0,0), (-1,-1), 0.25, colors.grey)]))
	story.append(ch_tbl)
	story.append(Spacer(1, 12))

	# Loyalty history
	story.append(Paragraph('Loyalty Points History', styles['Heading2']))
	lh_data = [['Date', 'Type', 'Points', 'Note']]
	for l in loyalty_history:
		lh_data.append([l.get('date').strftime('%Y-%m-%d %H:%M') if l.get('date') else '', l.get('type', ''), str(l.get('points', 0)), l.get('note', '')[:80]])
	if len(lh_data) == 1:
		lh_data.append(['-', '-', '-', 'No loyalty history'])
	lh_tbl = Table(lh_data, hAlign='LEFT', colWidths=[35*mm, 40*mm, 25*mm, 80*mm])
	lh_tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')), ('GRID', (0,0), (-1,-1), 0.25, colors.grey)]))
	story.append(lh_tbl)

	try:
		doc.build(story)
	except Exception as e:
		return HttpResponse(f'Failed to generate PDF: {e}', status=500)

	buffer.seek(0)
	# Return as attachment
	return FileResponse(buffer, as_attachment=True, filename='my_profile_report.pdf')


@login_required
def customer_add_deferred_credit(request):
	"""Allow a customer to add deferred credit themselves (creates a debt entry).

	This endpoint accepts POST with JSON { amount, note } and creates a
	pos.CreditTransaction (if available) and updates the user's credit_balance.
	"""
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

	try:
		data = json.loads(request.body)
	except Exception:
		return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

	amount = data.get('amount')
	note = data.get('note', 'Customer requested deferred credit')

	try:
		from decimal import Decimal, InvalidOperation
		amt = Decimal(str(amount))
	except (InvalidOperation, TypeError, ValueError):
		return JsonResponse({'success': False, 'error': 'Invalid amount'}, status=400)

	if amt <= Decimal('0'):
		return JsonResponse({'success': False, 'error': 'Amount must be positive'}, status=400)

	# Apply credit (this increases customer's owed balance)
	try:
		request.user.add_credit(amt)

		# Try to log in pos.CreditTransaction
		try:
			from pos.models import CreditTransaction as PosCT
			PosCT.objects.create(
				user=request.user,
				amount=amt,
				action='add',
				balance_after=request.user.credit_balance,
				note=note,
				staff=None
			)
		except Exception:
			# Fallback to loyalty model if pos not available
			try:
				from loyalty.models import CreditTransaction as LoyaltyCT
				LoyaltyCT.objects.create(
					customer=request.user,
					transaction_type='credit_added',
					amount=amt,
					description=note
				)
			except Exception:
				pass

		return JsonResponse({'success': True, 'new_balance': str(request.user.credit_balance)})
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def customer_credit_history(request):
	"""Return consolidated credit history for the logged-in customer."""
	try:
		# Fetch pos transactions
		txns = []
		try:
			from pos.models import CreditTransaction as PosCT
			pos_qs = PosCT.objects.filter(user=request.user).order_by('-created_at')[:500]
			for t in pos_qs:
				txns.append({
					'source': 'pos',
					'id': t.id,
					'amount': str(t.amount),
					'action': t.action,
					'note': t.note,
					'balance_after': str(t.balance_after),
					'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
				})
		except Exception:
			pass

		try:
			from loyalty.models import CreditTransaction as LoyaltyCT
			loy_qs = LoyaltyCT.objects.filter(customer=request.user).order_by('-created_at')[:500]
			for t in loy_qs:
				txns.append({
					'source': 'loyalty',
					'id': t.id,
					'amount': str(t.amount),
					'action': getattr(t, 'transaction_type', 'unknown'),
					'note': getattr(t, 'description', ''),
					'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
				})
		except Exception:
			pass

		# Sort combined txns by created_at desc
		txns.sort(key=lambda x: x.get('created_at', ''), reverse=True)

		return JsonResponse({'success': True, 'transactions': txns})
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def dashboard_status(request):
	"""Return JSON with minimal status for realtime polling."""
	from django.http import JsonResponse
	data = {
		'credit_balance': str(request.user.credit_balance),
		'loyalty_points': request.user.loyalty_points,
	}
	return JsonResponse(data)


@login_required
def customer_orders(request):
	return render(request, 'users/orders.html')


def verify_email(request, token=None):
	"""Verification disabled: redirect to login."""
	messages.info(request, 'Email verification has been disabled. You can log in using your email and password.')
	return redirect('users:login')


def resend_verification(request):
	"""Verification disabled: redirect to login."""
	messages.info(request, 'Email verification has been disabled. You can log in using your email and password.')
	return redirect('users:login')


def password_reset_request(request):
	"""Handle password reset request"""
	if request.method == 'POST':
		form = CustomPasswordResetForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			try:
				user = User.objects.get(email=email)
				send_password_reset_email(user, request)
				messages.success(
					request,
					'Password reset link has been sent to your email.'
				)
				return redirect('users:login')
			except User.DoesNotExist:
				messages.error(request, 'No account found with this email.')
	else:
		form = CustomPasswordResetForm()
	
	return render(request, 'users/password_reset_form.html', {'form': form})


def password_reset_confirm(request, token):
	"""Handle password reset confirmation"""
	user, error = verify_token(token)
	if not user:
		messages.error(request, error or 'Invalid or expired reset link')
		return redirect('users:login')
	
	if request.method == 'POST':
		form = ResetPasswordForm(request.POST)
		if form.is_valid():
			user.set_password(form.cleaned_data['new_password1'])
			user.email_verification_token = None
			user.token_expiry = None
			user.save()
			messages.success(request, 'Password has been reset successfully.')
			return redirect('users:login')
	else:
		form = ResetPasswordForm()
	
	return render(request, 'users/password_reset_confirm.html', {
		'form': form,
		'token': token
	})
