# Generated by Django 3.0 on 2024-02-14 08:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_wishlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.IntegerField()),
                ('qty', models.IntegerField()),
                ('total_price', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User')),
                ('watch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Watch')),
            ],
        ),
    ]