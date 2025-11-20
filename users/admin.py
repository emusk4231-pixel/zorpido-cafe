from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, CustomerMessage
from django.http import HttpResponse

try:
	from reportlab.lib.pagesizes import A4
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib import colors
	from reportlab.lib.units import mm
except Exception:
	SimpleDocTemplate = None


def export_users_as_pdf(modeladmin, request, queryset):
	if SimpleDocTemplate is None:
		return HttpResponse('reportlab not installed. Install reportlab to enable PDF export.', status=500)

	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
	styles = getSampleStyleSheet()
	story = [Paragraph('User List Export', styles['Heading1']), Spacer(1, 6)]

	data = [['ID', 'Full Name', 'Email', 'Phone', 'Location', 'Loyalty', 'Earned', 'Credit', 'Created']]
	for u in queryset.order_by('id'):
		data.append([
			str(u.id),
			u.full_name or '',
			u.email or '',
			u.phone or '',
			u.location or '',
			str(getattr(u, 'loyalty_points', 0) or 0),
			str(getattr(u, 'total_points_earned', 0) or 0),
			f"{(u.credit_balance or 0):.2f}",
			u.created_at.strftime('%Y-%m-%d') if getattr(u, 'created_at', None) else ''
		])

	tbl = Table(data, hAlign='LEFT', colWidths=[18*mm, 45*mm, 60*mm, 30*mm, 45*mm, 18*mm, 18*mm, 24*mm, 24*mm])
	tbl.setStyle(TableStyle([
		('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
		('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
		('GRID', (0,0), (-1,-1), 0.25, colors.grey),
		('VALIGN', (0,0), (-1,-1), 'MIDDLE')
	]))
	story.append(tbl)

	try:
		doc.build(story)
	except Exception as e:
		return HttpResponse(f'Failed to generate PDF: {e}', status=500)

	buffer.seek(0)
	response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="users_export.pdf"'
	return response


from io import BytesIO


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	"""Use Django's built-in UserAdmin to expose permissions and groups."""
	model = User
	list_display = ('username', 'full_name', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'created_at')
	list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups')
	search_fields = ('username', 'full_name', 'email')
	readonly_fields = ('created_at', 'updated_at')

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('full_name', 'email', 'phone', 'date_of_birth', 'location')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')
		}),
	)

	ordering = ('email',)
	filter_horizontal = ('groups', 'user_permissions')
	actions = ['export_users_as_pdf']
	export_users_as_pdf.short_description = 'Export selected users to PDF'


@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'replied')
	list_filter = ('is_read', 'replied', 'created_at')
	search_fields = ('name', 'email', 'subject')
