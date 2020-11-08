# Generated by Django 3.1.1 on 2020-10-01 04:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.CharField(max_length=5000)),
                ('feedbackDate', models.DateField(auto_now_add=True)),
                ('feedbackTime', models.TimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('feedbackTo_LoginId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedbackTo_LoginId', to='login.loginmaster')),
                ('productId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productId', to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='Complain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complainSubject', models.CharField(max_length=500)),
                ('complainDescription', models.CharField(max_length=5000)),
                ('complainDate', models.DateField(auto_now_add=True)),
                ('complainTime', models.TimeField(auto_now_add=True)),
                ('complainStatus', models.CharField(max_length=50)),
                ('replySubject', models.CharField(max_length=500)),
                ('replyMessage', models.CharField(max_length=5000)),
                ('replyDate', models.DateField(null=True)),
                ('replyTime', models.TimeField(null=True)),
                ('complainFrom_LoginId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complainFrom_LoginId', to='login.loginmaster')),
                ('complainTo_LoginId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complainTo_LoginId', to='login.loginmaster')),
            ],
        ),
    ]
