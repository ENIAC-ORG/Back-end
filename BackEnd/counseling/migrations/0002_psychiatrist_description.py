

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counseling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='psychiatrist',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
