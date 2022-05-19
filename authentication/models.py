from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
import phonenumbers
from rest_framework.exceptions import APIException
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Model to store local users in the database.
    """
    
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{str(self.first_name)} {str(self.last_name)}"
    
    def fullname(self):
        return f"{str(self.first_name)} {str(self.last_name)}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            self.clean()
        except ValidationError as e:
            raise APIException(str(e))
        super(User, self).save()

class Profile(models.Model):
    INTERN = 1
    SUPERVISOR = 2
    ROLE_CHOICES = (
        (INTERN, 'Intern'),
        (SUPERVISOR, 'Supervisor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30,blank=True,null=True)
    birthdate = models.DateField(blank=True,null=True)
    position = models.CharField(max_length=64,blank=True,null=True)
    descriptions = models.CharField(max_length=255, blank=True, default='')
    phonenumbers = models.CharField(max_length=14,blank=True,null=True, unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1)

    join_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.email

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Profile'