from django.shortcuts import render
import json
from django.shortcuts import redirect
import json
import os
from robot_communication.models import Sys_user,Communication
from django.contrib.auth.models import User
from django.contrib import auth
# import tensorflow as tf
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import redirect,HttpResponseRedirect
from django.http import JsonResponse,HttpResponse
import copy
import datetime
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
# Create your views here.

def index(request):
    if request.method=='GET':
        return render(request,'login.html', {'wrong': 0})


def loginf(request):
    if request.method == "POST":
        loginname = request.POST['username']
        loginpassword = request.POST['pwd']
        user = auth.authenticate(username=loginname, password=loginpassword)
        # print(loginname)
        # print(loginpassword)
        if user is not None:
            login(request, user)
            sys_user = Sys_user.objects.get(user=user)
            communication_list = Communication.objects.order_by("date")
            # for i in communication_list:
            #     print(i.com_content)
            return render(request, 'index.html', {'user': user, 'sys_user':sys_user,'communication_list':communication_list})
        else:
            return render(request, 'login.html', {'wrong': 1})

def regist(request):
    if request.method=='GET':
        return render(request, 'regist.html')
    if request.method=='POST':
        registnum = request.POST['username']
        todouser = User.objects.filter(username=registnum)
        if todouser.exists():
            logininfo = "same_error"
            return render(request, 'regist.html', {'logininfo': logininfo})
        else:
            registpassword = request.POST['pwd']
            nicheng = request.POST['nicheng']
            registemail = request.POST['email']
            # print(sex)
            # print(profession)
            if User.objects.filter(email=registemail):
                logininfo = "repeate"
                return render(request, 'regist.html', {'logininfo': logininfo})

            else:
                try:
                    validate_email(registemail)
                    todo = User.objects.create_user(registnum, registemail, registpassword)
                    todo.save()
                    todom = Sys_user(user=todo, name=nicheng,email=registemail)
                    todom.save()
                    loginflag = 'regist_sucsess'
                    return render(request, 'login.html', {'loginflag': loginflag , 'loginnum':registnum })
                except ValidationError:
                    logininfo = 'wrong'
                    return render(request, 'regist.html', {'logininfo': logininfo})


def robot_response(request):
    dt=datetime.datetime.now()
    print(dt)
    if request.method=='GET':
        # print("get了")
        my_text=request.GET.get("my_text")    #此处为算法输入
        print(my_text)
        new_content_my=Communication(com_type="human",com_content=my_text)
        new_content_my.save()
        #插入后端算法，我这里使用了一个candidate列表来代替
        candidate_list=['感冒','发烧','腮腺炎']
        import random


        # dt_time=dt.strftime('%Y-%m-%d %H:%M:%S')
        # print(dt_time)
        robot_response=random.choice(candidate_list)   #此处更换为后端算法的输出

        new_content_robot = Communication(com_type="robot", com_content=robot_response)
        new_content_robot.save()
        # from django.core import serializers
        # new_content_robot = serializers.serialize("json", new_content_robot)
        # new_content_robot=json.dumps(new_content_robot)
        # print(new_content_robot.date)
        content_time=str(new_content_robot.date).split('.')[0].replace('\t',' ')
        ret={
            'time':content_time,
            'content':new_content_robot.com_content
        }
        return JsonResponse(ret,safe=False)

def logoutf(request):
    logout(request)
    return render(request, 'login.html')

def delete_all(request):
    if request.method=='GET':
        user=request.user
        Communication.objects.all().delete()
        sys_user = Sys_user.objects.get(user=user)
        communication_list = Communication.objects.order_by("date")
        # for i in communication_list:
        #     print(i.com_content)
        return render(request, 'index.html', {'user': user, 'sys_user': sys_user, 'communication_list': communication_list})
# def ajax_demo1(request):
#     return render(request, "ajax_demo1.html")
#
#
# def ajax_add(request):
#     i1 = int(request.GET.get("i1"))
#     i2 = int(request.GET.get("i2"))
#     ret = i1 + i2
#     return JsonResponse(ret, safe=False)
