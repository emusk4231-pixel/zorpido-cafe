from django.db import models
from cloudinary.models import CloudinaryField
from utils.supabase_storage import upload_file


class Testimonial(models.Model):
	"""Customer testimonials shown on the homepage. Admin-manageable."""
	customer_name = models.CharField(max_length=200)
	message = models.TextField()
	rating = models.PositiveSmallIntegerField(default=5)
	# Store public URL returned by Supabase Storage
	profile_picture = CloudinaryField('profile_picture', blank=True, null=True)

	def set_profile_picture_from_file(self, file_obj, file_name: str = None):
		"""Upload file to Supabase and set `profile_picture` to public URL."""
		if file_name is None:
			file_name = getattr(file_obj, 'name', 'testimonials/unnamed')
		url = upload_file(file_obj, file_name)
		self.profile_picture = url
		self.save(update_fields=['profile_picture'])
	is_active = models.BooleanField(default=True, help_text='Show this testimonial on the homepage')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Testimonial'
		verbose_name_plural = 'Testimonials'

	def __str__(self):
		return f"{self.customer_name} ({self.rating}★)"


class FeaturedImage(models.Model):
	"""Images used in the homepage featured slider. Admin-managed."""
	title = models.CharField(max_length=200, blank=True)
 	# Store public URL for featured image
	image = CloudinaryField('image', help_text='Recommended: 1280x720 (16:9)')

	def set_image_from_file(self, file_obj, file_name: str = None):
		if file_name is None:
			file_name = getattr(file_obj, 'name', 'featured/unnamed')
		url = upload_file(file_obj, file_name)
		# `upload_file` returns a URL when using default_storage; assign
		# so legacy callers and templates continue to work.
		self.image = url
		self.save(update_fields=['image'])
	order = models.IntegerField(default=0, help_text='Lower numbers show first')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['order', '-created_at']
		verbose_name = 'Featured Image'
		verbose_name_plural = 'Featured Images'

	def __str__(self):
		return self.title or f'Featured Image {self.pk}'

	def clean(self):
		# Attempt to validate image dimensions if Pillow is available
		try:
			from PIL import Image
			self.image.open()
			img = Image.open(self.image)
			w, h = img.size
			# prefer 16:9 (1280x720) but don't enforce strictly; warn if very different
			if w < 800 or h < 450:
				from django.core.exceptions import ValidationError
				raise ValidationError('Image resolution is too small; recommended 1280x720 or larger (16:9).')
		except Exception:
			# If PIL not installed or image not accessible yet, skip strict validation
			pass
