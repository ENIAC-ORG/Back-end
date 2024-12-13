

import django.utils.timezone

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='date',
            field=models.DateField(null=True),

        ),
    ]
