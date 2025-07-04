# Generated by Django 5.0.12 on 2025-05-06 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Local_Church', '0002_report_attendance_teens'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='attendance',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='attendance',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='big_day',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='big_day',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='big_day',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='cash_transactions',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='cash_transactions',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='cash_transactions',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='mission_offering',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='mission_offering',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='mission_offering',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='plot_buying',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='Unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='plot_buying',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='plot_buying',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='ussd_transactions',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='ussd_transactions',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='ussd_transactions',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AddField(
            model_name='visitors',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='visitors',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AddField(
            model_name='visitors',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
        migrations.AlterField(
            model_name='report',
            name='approved_by',
            field=models.CharField(blank=True, default='Bishop Ben Irungu', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='church_name',
            field=models.CharField(choices=[('Murangá Church', 'Murangá Church')], default='unknown', max_length=100),
        ),
        migrations.AlterField(
            model_name='report',
            name='district_name',
            field=models.CharField(default='MT. KENYA WEST DISTRICT', max_length=100),
        ),
        migrations.AlterField(
            model_name='report',
            name='section_name',
            field=models.CharField(default='MURANGÁ SECTION', max_length=100),
        ),
    ]
