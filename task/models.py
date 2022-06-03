from email.policy import default
import profile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from authentication.models import Profile

# Create your models here.
class Task(models.Model):

    created_by = models.ForeignKey(
        Profile, 
        related_name='users', 
        on_delete=models.CASCADE, 
        verbose_name=_('User')
    )

    title = models.CharField(_('Title'), max_length=100)
    description = models.TextField(_('Description'))
    dead_line = models.DateField()

    assign_to = models.ManyToManyField(Profile,blank=True,through='task_assign')

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    status = models.JSONField(default=list, null=True, blank=True)
    
    class Meta:
        ordering = ('title', )
        verbose_name = 'task'
        verbose_name_plural = 'tasks'
   
    def __str__(self):
        return str(self.title)
    

class task_assign(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE )
    rank = models.PositiveIntegerField(blank=True, null=True)
