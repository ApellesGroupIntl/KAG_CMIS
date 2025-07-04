# Generated by Django 5.0.12 on 2025-05-20 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USSD_CORE', '0003_alter_transactions_txn_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='UssdUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('dob', models.DateField()),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
