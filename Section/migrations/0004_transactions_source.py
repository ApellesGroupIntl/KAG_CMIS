# Generated by Django 5.0.12 on 2025-06-14 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Section', '0003_transactions_date_transactions_week_of_month_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='source',
            field=models.CharField(default='section', max_length=20),
        ),
    ]
