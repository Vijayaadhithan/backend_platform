from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_booking_cancellation_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language_preference',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('de', 'German'), ('hi', 'Hindi')], default='en', max_length=2),
        ),
    ]