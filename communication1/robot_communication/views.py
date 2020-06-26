from django.shortcuts import render
import json
from django.shortcuts import redirect
import json
import os
from robot_communication.models import Sys_user, Communication
from util.nlp_utility import NLPUtility
from util.csv_utility import CsvUtility
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

def _get_dict(data, reverse=True):
    data_dict = {}
    if reverse:
        a = 1
        b = 0
    else:
        a = 0
        b = 1
    for i in data:
        sp = i.split("\t")
        if sp[a] in data_dict:
            data_dict[sp[a]].add(sp[b])
        else:
            data_dict[sp[a]] = set([sp[b]])
    return data_dict

def get_first_diag(chief_complaint, disease_dict, syptom_dict):
    nu_dis = NLPUtility(word_pattern_file=rootPath + "/data/load_dict_jieba.csv")
    nu_dis.load_jieba_model()
    diag_count = nu_dis.key_word_extract(chief_complaint, {**disease_dict, **syptom_dict})
    # print(diag_count)
    diag_list = [i[0] for i in sorted(diag_count.items(), key=lambda x: x[1], reverse=True)]

    robot_response = "最有可能是：\"" + diag_list[0] + "\""
    if len(diag_list) > 1:
        robot_response += "，还有可能是："
        for diag_i in range(1, len(diag_list)):
            robot_response += "\"" + diag_list[diag_i] + "\""
            # if diag_i < len(diag_list) - 1:
            #     robot_response += "、"
            if diag_i < len(diag_list) - 1:
                robot_response += "、"
    return robot_response, diag_list

# 返回第diag_index个疾病的检验检查项
def get_labtest(diag_list, diag_index, phy_dict, labtest_dict):
    diag_now = diag_list[diag_index]
    labtest_result = []
    if diag_now in phy_dict:
        for phy_i in phy_dict[diag_now]:
            labtest_result.append(labtest_dict[phy_i])
    return labtest_result

# 根据用户的检验检查结果，与第diag_index个疾病的生理指标相匹配，满足条件返回True
def match_phy_condition(phy_result, diag_list, diag_index, phy_dict):
    nu_phy=NLPUtility(word_pattern_file=rootPath + "/data/生理指标实例.csv")
    nu_phy.load_jieba_model()
    phy_sub, phy_cond = nu_phy.condition_extract(phy_result, CsvUtility.read_norm_array_csv(rootPath + "/data/生理指标实例.csv"))
    for sub_i in range(len(phy_sub)):
        if phy_sub[sub_i]+"##"+phy_cond[sub_i] in phy_dict[diag_list[diag_index]]:
            return True
    return False

def robot_response(request):
    dt = datetime.datetime.now()
    print(dt)

    print("......加载模型中......")
    disease_dict = _get_dict(CsvUtility.read_norm_array_csv(rootPath + '/data/病史关系.csv'))
    syptom_dict = _get_dict(CsvUtility.read_norm_array_csv(rootPath + '/data/疾病症状关系.csv'))
    CsvUtility.write_word_dict(rootPath + '/data/load_dict_jieba.csv', list(disease_dict.keys()) + list(syptom_dict.keys()))
    # print(syptom_dict)
    phy_dict = _get_dict(CsvUtility.read_norm_array_csv(rootPath + '/data/疾病-指标条件关系.csv'), reverse=False)
    labtest_dict = _get_dict(CsvUtility.read_norm_array_csv(rootPath + '/data/生理指标-检验检查关系.csv'))
    print("......加载完成......")

    if request.method=='GET':
        # print("get了")
        my_text=request.GET.get("my_text")    #此处为算法输入
        print(my_text)
        new_content_my = Communication(com_type="human",com_content=my_text)
        new_content_my.save()

        robot_response, diag_list = get_first_diag(my_text, disease_dict, syptom_dict)
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