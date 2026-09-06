from django.db import models
from django.utils import timezone
from datetime import date
from .services import scheduling


class Member(models.Model):
    name = models.CharField(max_length=40)
    emoji = models.CharField(max_length=8, default='🧽')
    hue = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Chore(models.Model):
    RECURRING, ONEOFF = 'recurring', 'oneoff'
    DAILY, INTERVAL, WEEKLY = 'daily', 'interval', 'weekly'

    title = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=[(RECURRING, 'Recurring'), (ONEOFF, 'One-off')])
    freq_kind = models.CharField(max_length=10, blank=True)
    freq_interval = models.PositiveSmallIntegerField(default=1)
    freq_weekdays = models.JSONField(default=list)
    due_date = models.DateField()
    claimed_by = models.ForeignKey(Member, null=True, blank=True, on_delete=models.SET_NULL, related_name='claimed')
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.due_date < date.today()

    def advance(self):
        if self.kind == self.ONEOFF:
            self.archived = True
        else:
            self.due_date = scheduling.next_due(self.due_date, self.freq_kind, self.freq_interval, self.freq_weekdays)
        self.save()


class Completion(models.Model):
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    chore_title = models.CharField(max_length=120)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    on_time = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.chore_title:
            self.chore_title = self.chore.title
        super().save(*args, **kwargs)


class Miss(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='misses')
    date = models.DateField()

    class Meta:
        unique_together = (('member', 'date'),)


class Unlock(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='unlocks')
    kind = models.CharField(max_length=8)
    key = models.CharField(max_length=40)
    date = models.DateField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        unique_together = (('member', 'kind', 'key'),)
