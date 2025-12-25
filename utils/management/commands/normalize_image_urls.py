from django.core.management.base import BaseCommand
from django.conf import settings
from utils.supabase_storage import get_file_url

MODELS_AND_FIELDS = [
    ('users', 'User', 'profile_picture'),
    ('menu', 'MenuItem', 'image'),
    ('gallery', 'GalleryImage', 'image'),
    ('blogs', 'BlogPost', 'featured_image'),
    ('website', 'FeaturedImage', 'image'),
    ('website', 'Testimonial', 'profile_picture'),
]

class Command(BaseCommand):
    help = 'Normalize stored image fields to full public URLs (safe dry-run available).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Apply changes; without this flag runs a dry-run')
        parser.add_argument('--bucket', type=str, help='Optional bucket name to use when constructing URLs')

    def handle(self, *args, **options):
        apply = options.get('apply')
        bucket = options.get('bucket')
        total = 0
        updated = 0
        self.stdout.write('Starting image URL normalization (dry-run=%s)' % (not apply,))
        for app_label, model_name, field in MODELS_AND_FIELDS:
            try:
                from django.apps import apps
                Model = apps.get_model(app_label, model_name)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping {app_label}.{model_name}: {e}"))
                continue
            qs = Model.objects.all()
            for obj in qs:
                total += 1
                val = getattr(obj, field, None)
                if not val:
                    continue
                s = str(val).strip()
                # If looks like a full URL already, skip
                if s.startswith('http://') or s.startswith('https://') or s.startswith('/'):
                    continue
                # Treat as object path; generate public URL
                try:
                    url = get_file_url(s, bucket=bucket)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to generate URL for {app_label}.{model_name}.{obj.pk}: {e}"))
                    continue
                self.stdout.write(f"Would update {app_label}.{model_name}({obj.pk}).{field}: {s} -> {url}")
                if apply:
                    setattr(obj, field, url)
                    obj.save(update_fields=[field])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {total} objects; updated {updated} (apply={apply})"))
