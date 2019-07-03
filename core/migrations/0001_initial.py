# Generated by Django 2.1.2 on 2019-07-03 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, max_length=65535)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reverse_replies', to='core.Post')),
                ('to_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.Post')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='reply_posts',
            field=models.ManyToManyField(related_name='is_reply_to', through='core.Reply', to='core.Post'),
        ),
        migrations.AddField(
            model_name='ontology',
            name='contained_replies',
            field=models.ManyToManyField(related_name='belongs_to_ontologies', to='core.Reply'),
        ),
        migrations.AddField(
            model_name='ontology',
            name='root',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Post'),
        ),
    ]