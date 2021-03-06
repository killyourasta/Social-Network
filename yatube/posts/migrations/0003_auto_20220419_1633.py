# Generated by Django 2.2.16 on 2022-04-19 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220315_1621'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='group description', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Use a unique link', unique=True, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Enter field documentation', max_length=200, verbose_name='Заголовок'),
        ),
    ]
