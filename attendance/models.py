from django.db import models
from datetime import datetime,date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

User = get_user_model()
# Create your models here.
class Attendance(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'present'),
        ('absent', 'absent'),
        ('leave', 'leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date_time = models.DateField(blank=True,default = date.today)
    status = models.CharField(max_length=20, default=ATTENDANCE_STATUS[0][0], choices=ATTENDANCE_STATUS)
    leave_reason = models.TextField(blank=True, null=True)

    entry_time = models.DateTimeField(blank=True,null=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):

        if self.status == "present" and not self.entry_time:
            self.entry_time = datetime.now()

        super(Attendance, self).save(*args, **kwargs)
    
    def __str__(self):
        return "{0} {1} {2} {3}".format(self.date_time,self.status,self.entry_time,self.user.first_name)
    
    class Meta:
        unique_together = ('user', 'date_time',)