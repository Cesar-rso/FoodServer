# Generated by Django 3.2.7 on 2022-01-20 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='orders.payments'),
        ),
    ]
