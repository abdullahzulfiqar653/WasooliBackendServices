# Generated by Django 4.2.16 on 2025-03-14 17:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0005_invoice_membership_alter_invoice_due_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='code',
            field=models.CharField(editable=False, max_length=14, unique=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(default=datetime.date(2025, 3, 29)),
        ),
    ]
