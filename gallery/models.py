from django.db import models
from utils.supabase_storage import upload_file


class GalleryImage(models.Model):
	"""Image for the public gallery used on the website.

	This minimal model provides the fields `CATEGORY_CHOICES` and
	`is_active` that `website.views` expects.
	"""
	CATEGORY_CHOICES = (
		('food', 'Food'),
		('interior', 'Interior'),
		('event', 'Event'),
		('other', 'Other'),
		('feedback', 'Feedback'),

	)

	title = models.CharField(max_length=200, blank=True)
	# Store public URL returned by Supabase Storage
	image = models.URLField(max_length=500, null=True, blank=True, default='')

	def set_image_from_file(self, file_obj, file_name: str = None):
		if file_name is None:
			file_name = getattr(file_obj, 'name', 'gallery/unnamed')
		url = upload_file(file_obj, file_name)
		self.image = url
		self.save(update_fields=['image'])
	caption = models.TextField(blank=True)
	category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
	is_active = models.BooleanField(default=True)
	# Marks images that should appear in the homepage "Zorpido's Glimpses" section
	is_glimpses = models.BooleanField(default=False)
	# New field: mark images that should appear in the homepage "Zorpido's Glimpses" section
	is_zorpido_glimpses = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'Gallery Image'
		verbose_name_plural = 'Gallery Images'

	def __str__(self):
		return self.title or f'GalleryImage {self.pk}'
