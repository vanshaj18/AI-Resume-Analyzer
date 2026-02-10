from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ui", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysisrun",
            name="file_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
