# Generated by Django 4.2.16 on 2025-01-21 13:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_invoice_member_alter_invoice_due_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='amount_due',
            new_name='due_amount',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='amount',
            new_name='total_amount',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2025, 2, 5, 13, 11, 49, 84137, tzinfo=datetime.timezone.utc)),
        ),
    ]
