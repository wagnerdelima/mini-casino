# Generated by Django 2.2.3 on 2019-07-26 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Customer username', max_length=10)),
                ('password', models.CharField(help_text='Customer password', max_length=10)),
            ],
        ),
    ]
