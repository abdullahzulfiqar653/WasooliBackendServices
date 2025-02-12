# Generated by Django 4.2.16 on 2025-02-12 21:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0006_merchantmembership_total_saved_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='merchant',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='merchantmember',
            options={'verbose_name': 'Members Register'},
        ),
        migrations.AlterModelOptions(
            name='supplyrecord',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='invoice',
            name='type',
            field=models.CharField(choices=[('monthly', 'Monthly'), ('one_time', 'One Time'), ('other', 'Other'), ('miscellaneous', 'Miscellaneous')], default='monthly', max_length=15),
        ),
        migrations.AddField(
            model_name='merchant',
            name='area',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='merchant',
            name='city',
            field=models.CharField(default='rahim yar khan', max_length=128),
        ),
        migrations.AddField(
            model_name='merchant',
            name='is_advance_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2025, 2, 27, 21, 11, 11, 688927, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['-created_at'], name='apis_invoic_created_a075be_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['member', 'type'], name='apis_invoic_member__66a52b_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['member', 'status'], name='apis_invoic_member__66fcc8_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['member', 'created_at'], name='apis_invoic_member__c2b81f_idx'),
        ),
        migrations.AddIndex(
            model_name='merchant',
            index=models.Index(fields=['-created_at'], name='apis_mercha_created_165d0c_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['cnic'], name='apis_mercha_cnic_01421f_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['code'], name='apis_mercha_code_53d7fb_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['user'], name='apis_mercha_user_id_4b0611_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['merchant'], name='apis_mercha_merchan_93926e_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['-created_at'], name='apis_mercha_created_5cb7c9_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmember',
            index=models.Index(fields=['primary_phone'], name='apis_mercha_primary_84c355_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmembership',
            index=models.Index(fields=['account'], name='apis_mercha_account_948310_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmembership',
            index=models.Index(fields=['is_active'], name='apis_mercha_is_acti_71b6c0_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmembership',
            index=models.Index(fields=['is_monthly'], name='apis_mercha_is_mont_24430a_idx'),
        ),
        migrations.AddIndex(
            model_name='merchantmembership',
            index=models.Index(fields=['-created_at'], name='apis_mercha_created_c5b5d9_idx'),
        ),
        migrations.AddIndex(
            model_name='supplyrecord',
            index=models.Index(fields=['merchant_membership', 'created_at'], name='apis_supply_merchan_cbe570_idx'),
        ),
        migrations.AddIndex(
            model_name='supplyrecord',
            index=models.Index(fields=['-created_at'], name='apis_supply_created_6b22cf_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['type', 'created_at', 'transaction_type', 'merchant_membership'], name='apis_transa_type_b44a38_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['type', 'transaction_type', 'is_commission_paid', 'merchant_membership'], name='apis_transa_type_5b27ea_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['-created_at'], name='apis_transa_created_b28593_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['merchant', 'type', 'transaction_type'], name='apis_transa_merchan_4fcdbf_idx'),
        ),
    ]
