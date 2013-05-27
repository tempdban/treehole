#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# Created at Mar 20 18:38 by BlahGeek@Gmail.com

import sys
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding('UTF-8')

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from treehole.models import ContentModel, PlaceholderModel
from treehole.utils import checkIP, postStatu, MSG
from treehole.settings import LINKS
from datetime import datetime, timedelta
import logging
import random

def index(req):
    ipaddr = req.META.get('REMOTE_ADDR', '')
    _content = ''
    if req.method == 'POST':
        _content = req.POST.get('content', '')
        if not checkIP(ipaddr):
            messages.error(req, MSG['IP_NOT_VALID'])
        elif not (len(_content) < 120 and len(_content) > 5):
            messages.error(req, MSG['CONTENT_TOO_LONG'])
        elif ContentModel.objects.filter(ip=ipaddr, time__range=\
                (datetime.now()-timedelta(minutes=30), datetime.now())).count() > 0:
            messages.error(req, MSG['TOO_MANY_TIMES'])
        else:
            try:
                postStatu(_content, ipaddr)
            except:
                messages.error(req, MSG['PUBLISH_ERROR'])
                logging.error('Error in ' + str(ContentModel.objects.count()))
            else:
                messages.success(req, MSG['PUBLISH_OK'])
                _content = ''

# for doreamon icon
    try:
        icon = int(req.path[1:])
    except ValueError:
        icon = 0
    tourl = ''
    if icon == 0 or req.session.get('redirect', 0) == 0:
        req.session['redirect'] = 1
        tourl = '/' + str(random.randint(1, 16))
    else:
        req.session['redirect'] = 0
    isIphone = ('iPhone' in req.META.get('HTTP_USER_AGENT', '') and req.method == 'GET')
    return render_to_response('index.html', \
            {'ICO_NUM': icon, 'TOURL': tourl, 'ISIPHONE': isIphone, 
                'LINKS': LINKS, 
                'PLACEHOLER': PlaceholderModel.objects.order_by('?')[0].content, 
                'content': _content}, 
            context_instance=RequestContext(req))
