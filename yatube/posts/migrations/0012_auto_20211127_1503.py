# Generated by Django 2.2.16 on 2021-11-27 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Картинка поста', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]