# Generated by Django 2.1 on 2019-07-30 08:40

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bonus_money', models.FloatField(default=0.0, help_text='Customer bonus amount')),
                ('wagered', models.FloatField(default=0.0, help_text='Wagered amount that can be withdrawn')),
                ('wagering_requirement', models.FloatField(default=0.0, help_text='Wagering requirement')),
                ('casino_bonus_login', models.FloatField(default=100.0, help_text='Customer bonus amount given by log ins')),
                ('is_bonus_depleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_money', models.FloatField(default=0.0, help_text='Customer real amount of cash by deposits or wagered bonus.')),
                ('amount_lost', models.FloatField(default=0.0, help_text='Amount of real money lost on spins.')),
                ('casino_bonus_deposit', models.FloatField(default=20.0, help_text='Amount granted if customer deposits larger than 100 euros')),
                ('deposit_bonus_amount', models.FloatField(default=100.0, help_text='Amount of deposit to verify against. If customer deposits an amount larger than this field, we grant him a bonus of the field casino_bonus_deposit')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='casino.CustomerUser')),
            ],
        ),
        migrations.AddField(
            model_name='bonus',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='casino.CustomerUser'),
        ),
    ]
