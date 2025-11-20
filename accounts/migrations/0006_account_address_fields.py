from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='address_line_1',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='account',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='account',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='account',
            name='country',
            field=models.CharField(blank=True, default='India', max_length=50),
        ),
        migrations.AddField(
            model_name='account',
            name='pincode',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='account',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]

