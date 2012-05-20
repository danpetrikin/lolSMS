from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import re
import os.path
import hashlib
import uuid
    
class Contact(models.Model):
    phone = models.CharField(max_length=20)
    
class Group(models.Model):
    contacts = models.ManyToManyField(Contact)
    user = models.ForeignKey(User, verbose_name=_("user"))
    name = models.CharField(max_length=100)
    response = models.CharField(max_length=200)
    
class TwilioInfo(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"))
    account_sid = models.CharField(max_length=200)
    auth_token = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
