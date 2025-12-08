<<<<<<< HEAD
from django.db import models


class Testimonial(models.Model):
	"""Customer testimonials shown on the homepage. Admin-manageable."""
	customer_name = models.CharField(max_length=200)
	message = models.TextField()
	rating = models.PositiveSmallIntegerField(default=5)
	profile_picture = models.ImageField(upload_to='testimonials/', blank=True, null=True)
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
	image = models.ImageField(upload_to='featured/', help_text='Recommended: 1280x720 (16:9)')
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
=======
from django.db import models


class Testimonial(models.Model):
	"""Customer testimonials shown on the homepage. Admin-manageable."""
	customer_name = models.CharField(max_length=200)
	message = models.TextField()
	rating = models.PositiveSmallIntegerField(default=5)
	profile_picture = models.ImageField(upload_to='testimonials/', blank=True, null=True)
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
	image = models.ImageField(upload_to='featured/', help_text='Recommended: 1280x720 (16:9)')
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
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
