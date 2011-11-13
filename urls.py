from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required

import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^social/', include('socialregistration.urls',namespace = 'socialregistration')),                       
    (r'^accounts/', include('registration.urls')),
    url(r"^index/$", views.index, name="index"),
    url(r"^$", views.index, name="indexpage"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', login_required(views.home), name='home'),
    url(r'^ajax_send_text_message/', login_required(views.ajax_send_text_message), name='ajax_send_text_message'),
    url(r'^ajax_get_twilio_credentials/', login_required(views.ajax_get_twilio_credentials), name='ajax_get_twilio_credentials'),
    url(r'^ajax_new_group/', login_required(views.ajax_new_group), name='ajax_new_group'),
    url(r'^ajax_edit_group/', login_required(views.ajax_edit_group), name='ajax_edit_group'),
    url(r'^ajax_delete_group/', login_required(views.ajax_delete_group), name='ajax_delete_group'),
    url(r'^ajax_new_phone/', login_required(views.ajax_new_phone), name='ajax_new_phone'),
    url(r'^ajax_edit_phone/', login_required(views.ajax_edit_phone), name='ajax_edit_phone'),
    url(r'^ajax_delete_phone/', login_required(views.ajax_delete_phone), name='ajax_delete_phone'),
    url(r'^ajax_get_phones_for_group/', login_required(views.ajax_get_phones_for_group), name='ajax_get_phones_for_group'),
    url(r'^ajax_get_groups_for_user/', login_required(views.ajax_get_groups_for_user), name='ajax_get_groups_for_user'),
    url(r'^sms/(?P<user>[\w\.]+)/$', views.twil_response, name="twil_response"),
    url(r'^ajax_update_group_response/', login_required(views.ajax_update_group_response), name='ajax_update_group_response'),
    url(r'^ajax_get_group_response/', login_required(views.ajax_get_group_response), name='ajax_get_group_response'),
    # Examples:
    # url(r'^$', 'digitalstore.views.home', name='home'),
    # url(r'^digitalstore/', include('digitalstore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
