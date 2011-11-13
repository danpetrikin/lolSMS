import logging
import re
from random import choice
import string
from decimal import *
from annoying.decorators import render_to
from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponseServerError,\
    HttpRequest
from django.template.context import Context
from django.template.loader import get_template, TemplateDoesNotExist
from django.utils import simplejson as json
from django.contrib.auth.models import User
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from apps.lolSMS.models import *
from django.core.servers.basehttp import FileWrapper
from django.core.mail import EmailMultiAlternatives
import os
import stripe
from django.http import Http404
from settings import BASE_SMS_URL
from django.contrib.auth.models import User

from twilio.rest import TwilioRestClient


@render_to('index.html')
def index(request):
    return {'home': '/home/', }

@csrf_exempt
@render_to('twil_response.html')
def twil_response(request, user):
    usr = User.objects.get(id=user)
    message = request.POST.get('Body')
    user_phone = request.POST.get('From')
    g = Group()
    try:
        g = Group.objects.get(user = usr, name = message.upper())
    except:
        g.user = usr
        g.name = message.upper()
        g.response = 'Thanks for joining the ' + message + ' list'
        g.save()
    
    if message.upper() == "STOP":
        
        for co in Group.objects.filter(user = usr).contacts.all():
            if co.phone == user_phone[2:]:
                co.delete()
        return {'response' : 'You have been removed from our lists'}    
    
    found = 0
    for co in g.contacts.all():
        if co.phone == user_phone[2:]:
            found = 1
    
    
    if found == 0:
        c = Contact()
        c.phone = user_phone[2:]
        c.save()
        g.contacts.add(c)
        g.save()
    else:
        g = Group.objects.get(user = usr, name = message.upper())
    
    
    return {'response' : g.response}

@render_to('devhome.html')
def devhome(request):    
    if request.method == 'POST':
        user = request.user
        try:
            twil_info = TwilioInfo.objects.get(user=user)
            twil_info.account_sid = request.POST.get('account_sid')
            twil_info.auth_token = request.POST.get('auth_token')
            twil_info.phone = request.POST.get('send_phone')
            twil_info.save()
        except:
            twil_info = TwilioInfo()
            twil_info.account_sid = request.POST.get('account_sid')
            twil_info.auth_token = request.POST.get('auth_token')
            twil_info.phone = request.POST.get('send_phone')
            twil_info.user = user
            twil_info.save()
            
    return {'home': '/home/'}

@render_to('home.html')
def home(request):  
    if request.method == 'POST':
        user = request.user
        try:
            twil_info = TwilioInfo.objects.get(user=user)
            twil_info.account_sid = request.POST.get('account_sid').strip()
            twil_info.auth_token = request.POST.get('auth_token').strip()
            twil_info.save()
        except:
            twil_info = TwilioInfo()
            twil_info.account_sid = request.POST.get('account_sid').strip()
            twil_info.auth_token = request.POST.get('auth_token').strip()
            twil_info.user = user
            twil_info.save()
            
        twil_info = TwilioInfo.objects.get(user=request.user)
        client = TwilioRestClient(twil_info.account_sid, twil_info.auth_token)
    
        for number in client.phone_numbers.iter():
            print number
            number.update(sms_url = BASE_SMS_URL + str(request.user.id) + '/')
            twil_info.phone = number.phone_number
            twil_info.save()
    
            
    return {'home': '/home/'}

@csrf_exempt
def ajax_send_text_message(request):
    try:
        if request.method == 'POST':
            user = request.user
            twil_info = TwilioInfo.objects.get(user=user)
            client = TwilioRestClient(twil_info.account_sid, twil_info.auth_token)
            message = client.sms.messages.create(to='+1' + str(request.POST.get('phone')), from_= twil_info.phone,body= str(request.POST.get('message')))
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    
    except Exception as e:
        errormess = 'ERROR: %s' % e
        return HttpResponse(simplejson.dumps(errormess), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_get_twilio_credentials(request):
    try:
        if request.method == 'POST':
            user = request.user
            twil_info = TwilioInfo.objects.get(user=user)
            return HttpResponse(simplejson.dumps({'account_sid': twil_info.account_sid, 'auth_token': twil_info.auth_token, 'send_phone' : twil_info.phone}),mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps({'account_sid': '', 'auth_token': '', 'send_phone' : ''}),mimetype='application/json')  
    return HttpResponse(simplejson.dumps({'account_sid': '', 'auth_token': '', 'send_phone' : ''}),mimetype='application/json')


@csrf_exempt
def ajax_new_group(request):
    try:
        if request.method == 'POST':
            user = request.user
            g = Group()
            g.user = request.user
            g.name = request.POST.get('name').upper()
            g.save()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_edit_group(request):
    try:
        if request.method == 'POST':
            g = Group.objects.get(id = request.POST.get('id'))
            g.name = request.POST.get('name').upper()
            g.save()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_delete_group(request):
    try:
        if request.method == 'POST':
            g = Group.objects.get(id = request.POST.get('id'))
            g.delete()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')


@csrf_exempt
def ajax_new_phone(request):
    try:
        if request.method == 'POST':
            user = request.user
            g = Group.objects.get(id = request.POST.get('id'))
            c = Contact()
            c.phone = request.POST.get('name')
            c.save()
            g.contacts.add(c)
            g.save()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_edit_phone(request):
    try:
        if request.method == 'POST':
            c = Contact.objects.get(id = request.POST.get('id'))
            c.phone = request.POST.get('name')
            c.save()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_delete_phone(request):
    try:
        if request.method == 'POST':
            c = Contact.objects.filter(id = request.POST.get('id'))
            c.delete()
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')


@csrf_exempt
def ajax_get_groups_for_user(request):
    try:
        if request.method == 'POST':
            groups = {}
            for g in Group.objects.filter(user = request.user):
                groups[g.id] = g.name
                
            return HttpResponse(simplejson.dumps(groups), mimetype='application/json')
    except Exception as e:
        return HttpResponse(simplejson.dumps("failed"), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_get_phones_for_group(request):
    try:
        if request.method == 'POST':
            phones = {}
            for c in Group.objects.get(id = request.POST.get('id')).contacts.all():
                phones[c.id] = c.phone    
            return HttpResponse(simplejson.dumps(phones), mimetype='application/json')
    except Exception as e:
        return HttpResponse(simplejson.dumps(''.join(e)), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_update_group_response(request):
    try:
        if request.method == 'POST':
            g = Group.objects.get(id = request.POST.get('id'))
            g.response = request.POST.get('response')
            g.save()    
            return HttpResponse(simplejson.dumps("success"), mimetype='application/json')
    except Exception as e:
        return HttpResponse(simplejson.dumps(''.join(e)), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')

@csrf_exempt
def ajax_get_group_response(request):
    try:
        if request.method == 'POST':
            g = Group.objects.get(id = request.POST.get('id'))   
            return HttpResponse(simplejson.dumps(g.response), mimetype='application/json')
    except Exception as e:
        return HttpResponse(simplejson.dumps(''.join(e)), mimetype='application/json')
    return HttpResponse(simplejson.dumps("not a post"), mimetype='application/json')