from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token

# Create your views here.

import sys, os
import time
sys.path.insert(0, os.path.abspath('..'))
from sender.sender import Sender
from module.simple.simple import Simple
from module.psm.psm_sample import PSM

def fromJson(para, msgs):
    msgs = list(msgs.split(','))
    for msg in msgs:
        para[list(msg.split(':'))[0]] = list(msg.split(':'))[1]

def server(request):
    msgs = request.GET.get("msg")
    if msgs == "" or msgs is None:
        print("参数错误")
        return HttpResponse("error")
    else:
        para = {'id': int(time.time()*100000)}
        fromJson(para, msgs)      

        if para['module'] == 'psm':
            psm = PSM(para['password'])
            return HttpResponse(psm.evaluate())
        else:
            simple = Simple(para)
            simple.predict()

            sender = Sender()
            sender.add_receivers(para['email'])
            sender.get_message(os.path.abspath(os.path.join('result', str(para['id'])+'.txt')))
            sender.send()
            return HttpResponse(para['id'])
