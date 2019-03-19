# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.db.models import signals
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


# Create your models here
class Trademark(TimeStampedModel):
    uan = models.IntegerField(unique=True)
    word = models.CharField(max_length=100)
    image = models.ImageField()

    def __str__(self):
        return '{0}'.format(self.uan)


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trademark = models.ManyToManyField(Trademark)

    def __str__(self):
        return '{0}'.format(self.user)


class Task(TimeStampedModel):
    STATUS_PENDING = 0
    STATUS_EXPIRED = 1
    STATUS_CHOICES = (
        (STATUS_PENDING, 'PENDING'),
        (STATUS_EXPIRED, 'EXPIRED')
    )

    URGENCY_LOW = 0
    URGENCY_MED = 1
    URGENCY_HIGH = 2
    URGENCY_CHOICES = (
        (URGENCY_LOW, 'LOW'),
        (URGENCY_MED, 'MEDIUM'),
        (URGENCY_HIGH, 'HIGH')
    )

    title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    trademark = models.ForeignKey(Trademark, null=True, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    urgency = models.IntegerField(choices=URGENCY_CHOICES, default=0)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}'.format(self.title)

    def save(self, **kwargs):
        self.decide_urgency()
        super(Task, self).save(**kwargs)

    def clean(self):
        if self.due_date < timezone.now():
            raise ValidationError("Due Date can't be in past!")

    def decide_urgency(self):
        current_datetime = timezone.now()
        delta = self.due_date - current_datetime

        if delta <= timedelta(days=1):
            self.urgency = self.URGENCY_HIGH
        elif timedelta(days=1) < delta <= timedelta(days=3):
            self.urgency = self.URGENCY_MED
        else:
            self.urgency = self.URGENCY_LOW


class Reminder(TimeStampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    firing_time = models.DateTimeField()
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return '{0} {1}'.format(self.task, self.firing_time)


@receiver(signals.post_save, sender=Task)
def create_reminder(sender, instance, created, **kwargs):
    if created:
        delta = instance.due_date - timezone.now()

        if delta >= timedelta(days=1):
            urgent_reminder = Reminder(task=instance, firing_time=instance.due_date - timedelta(days=1))
            urgent_reminder.save()

        if delta >= timedelta(days=5):
            gentle_reminder = Reminder(task=instance, firing_time=instance.due_date - timedelta(days=5))
            gentle_reminder.save()
