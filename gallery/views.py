<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
import os
from .models import GalleryImage

def download_image(request, image_id):
	"""Serve the gallery image file as an attachment for download."""
	image = get_object_or_404(GalleryImage, pk=image_id)
	if not image.image or not image.image.path:
		raise Http404("Image not found")

	file_path = image.image.path
	filename = os.path.basename(file_path)
	try:
		return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
	except FileNotFoundError:
		raise Http404("File does not exist")
=======
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
import os
from .models import GalleryImage

def download_image(request, image_id):
	"""Serve the gallery image file as an attachment for download."""
	image = get_object_or_404(GalleryImage, pk=image_id)
	if not image.image or not image.image.path:
		raise Http404("Image not found")

	file_path = image.image.path
	filename = os.path.basename(file_path)
	try:
		return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
	except FileNotFoundError:
		raise Http404("File does not exist")
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
