from __future__ import absolute_import, unicode_literals
from celery import task
from .models import Reminder
from django.utils import timezone


@task()
def send_notification():
    unsent_reminders = Reminder.objects.filter(firing_time__lte=timezone.now(), notification_sent=False)

    if unsent_reminders:
        print "Notification sent"
        unsent_reminders.update(notification_sent=True)
