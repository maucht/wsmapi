from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class DailyStats(models.Model):
    idKey = models.CharField(max_length=16, default='')

    posStat = models.IntegerField(default=0)
    negStat = models.IntegerField(default=0)