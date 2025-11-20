from django.contrib import admin
from .models import LoyaltyTransaction, LoyaltyProgram
from django.http import HttpResponse
from io import BytesIO

try:
	from reportlab.lib.pagesizes import A4
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib import colors
	from reportlab.lib.units import mm
except Exception:
	SimpleDocTemplate = None


def export_loyalty_as_pdf(modeladmin, request, queryset):
	if SimpleDocTemplate is None:
		return HttpResponse('reportlab not installed. Install reportlab to enable PDF export.', status=500)

	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
	styles = getSampleStyleSheet()
	story = [Paragraph('Loyalty Transactions Export', styles['Heading1']), Spacer(1, 6)]

	data = [['ID', 'Customer', 'Type', 'Points', 'Description', 'Order', 'Created']]
	for t in queryset.order_by('created_at'):
		data.append([
			str(t.id),
			(t.customer.full_name or t.customer.email) if t.customer else '',
			t.get_transaction_type_display(),
			str(t.points),
			(t.description or '')[:60],
			str(t.order.id) if getattr(t, 'order', None) else '',
			t.created_at.strftime('%Y-%m-%d %H:%M') if getattr(t, 'created_at', None) else ''
		])

	tbl = Table(data, hAlign='LEFT', colWidths=[12*mm, 45*mm, 30*mm, 18*mm, 70*mm, 20*mm, 30*mm])
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
	response['Content-Disposition'] = 'attachment; filename="loyalty_transactions_export.pdf"'
	return response



@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
	list_display = ('customer', 'transaction_type', 'points', 'created_at')
	list_filter = ('transaction_type', 'created_at')
	search_fields = ('customer__full_name',)
	actions = ['export_loyalty_as_pdf']


export_loyalty_as_pdf.short_description = 'Export selected loyalty transactions to PDF'


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
	list_display = ('name', 'points_per_rupee', 'redemption_rate', 'is_active')
	list_filter = ('is_active',)
