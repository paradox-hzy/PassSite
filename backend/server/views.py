import imp
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token

# Create your views here.

import sys, os
import time
sys.path.insert(0, os.path.abspath('..'))
from sender.sender import Sender
from module.LSTM.beam_search import LSTM
from module.PL.PLmodel import PL
from module.PassGAN.PassGAN import PassGAN
from module.simple.simple import Simple
from module.psm.main import PSM

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
        para = {'id': str(time.time_ns())}
        fromJson(para, msgs)      

        if para['module'] == 'psm':
            psm = PSM(para['password'])
            return HttpResponse(str(int(float(psm.evaluate()))))
        else:
            if para['module'] == 'lstm':
                lstm = LSTM(para)
                lstm.predict()
            elif para['module'] == 'pl':
                pl = PL(para)
                pl.predict()
            elif para['module'] == 'gan':
                passgan = PassGAN(para)
                passgan.predict()
            else:
                simple = Simple(para)
                simple.predict()

            sender = Sender()
            sender.add_receivers(para['email'])
            sender.get_message(os.path.abspath(os.path.join('result', str(para['id'])+'.txt')))
            sender.send()
            return HttpResponse(para['id'])
