# coding=utf-8
from __future__ import unicode_literals
import os
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Los usuarios deben de tener un correo')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True, help_text=_("Obligatorio"))
    first_name = models.CharField(_('first name'), max_length=35, blank=True)
    last_name = models.CharField(_('last name'), max_length=35, blank=True)
    second_last_name = models.CharField(_('Apellido Materno'), max_length=140, blank=True)

    telephone = models.CharField(max_length=20)

    activation_key = models.CharField(max_length=40, blank=True)

    key_expires = models.DateTimeField(default=timezone.now)

    has_verified_email = models.BooleanField(default=False, help_text='Indica si el usuario ha verificado su mail.')

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))

    date_joined = models.DateTimeField(default=timezone.now)

    foto_perfil = models.ImageField(max_length=300, upload_to='profile_pics',
                                    default=os.path.join(settings.STATIC_URL, 'images', 'default_avatar.jpg'),
                                    blank=True, null=True)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def natural_key(self):

        return (self.first_name, self.last_name, self.second_last_name, str(self.foto_perfil_url))

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    @property
    def foto_perfil_url(self):
        # Pseudocode:
        if self.foto_perfil == os.path.join(settings.STATIC_URL, 'images', 'default_avatar.jpg'):

            return self.foto_perfil

        else:

            return self.foto_perfil.url

    def user_groups(self):
        return self.groups.all().values_list('name', flat=True)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s %s' % (self.first_name, self.last_name, self.second_last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        # Simplest possible answer: Yes, always
        return True

    def user_group(self):
        return self.groups.get()

    def __unicode__(self):
        return self.email
