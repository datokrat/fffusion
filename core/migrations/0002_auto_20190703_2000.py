# Generated by Django 2.1.2 on 2019-07-03 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ontology',
            name='contained_replies',
        ),
        migrations.RemoveField(
            model_name='ontology',
            name='root',
        ),
        migrations.DeleteModel(
            name='Ontology',
        ),
    ]