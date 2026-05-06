from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_hotel_image'),
        ('core', '0004_merge_20260506_0449'), # Ensure these match your previous migration numbers
    ]

    operations = [
    ]