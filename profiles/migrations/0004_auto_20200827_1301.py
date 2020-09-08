# Generated by Django 3.1 on 2020-08-27 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_auto_20200827_1301'),
        ('profiles', '0003_auto_20200825_0142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='starred_articles',
        ),
        migrations.AddField(
            model_name='profile',
            name='favorite_articles',
            field=models.ManyToManyField(blank=True, related_name='favorited', to='articles.Article'),
        ),
    ]