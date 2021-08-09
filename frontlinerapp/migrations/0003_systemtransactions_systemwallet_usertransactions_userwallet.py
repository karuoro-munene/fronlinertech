# Generated by Django 3.2.4 on 2021-08-09 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('frontlinerapp', '0002_profile_referral'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_balance', models.IntegerField()),
                ('direct_earnings', models.IntegerField(null=True)),
                ('spill_earnings', models.IntegerField(null=True)),
                ('pending_spills', models.IntegerField(null=True)),
                ('pending_cashout', models.IntegerField(null=True)),
                ('settled_cashout', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('type', models.CharField(choices=[('PAY', 'PAY'), ('RECEIVE', 'RECEIVE')], max_length=10, null=True)),
                ('from_who', models.CharField(max_length=50, null=True)),
                ('transaction_type', models.CharField(choices=[('PAY', 'PAY'), ('RECEIVE', 'RECEIVE')], max_length=10, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_balance', models.IntegerField()),
                ('level_one_earnings', models.IntegerField(null=True)),
                ('level_two_earnings', models.IntegerField(null=True)),
                ('level_three_earnings', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('type', models.CharField(choices=[('ONE', 'ONE'), ('TWO', 'TWO'), ('THREE', 'THREE'), ('WITHDRAWAL', 'WITHDRAWAL')], max_length=10, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]