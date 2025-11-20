from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_user_email_verification_token_user_is_email_verified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
