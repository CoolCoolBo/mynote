from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import User
import hashlib

# Create your views here.
def reg_view(request):

    # 基础注册功能
    if request.method == 'GET':
        return render(request, 'user/register.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']

        if not username:
            return HttpResponse('账户名不能为空')
        if password_1 != password_2:
            return HttpResponse('两次输入的密码不一致')

        # 密码哈希
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()

        olduser = User.objects.filter(username=username)
        if olduser:
            return HttpResponse('用户名已存在!')

        # 此处同时插入有可能会报错，唯一索引注意并发写入问题
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            print('--cerete user error %s' % (e))
            return HttpResponse('用户名已存在!')
        
        # session设置免登录一天
        request.session['username'] = username
        request.session['uid'] = user.id

        return HttpResponse('注册成功！')

def login_view(request):

    if request.method == 'GET':
        # 登录状态检查
        # 先检查是否有session
        if request.session.get('username') and request.session.get('uid'):
            return HttpResponseRedirect('/index')
        # 再检查是否有cookies
        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username or c_uid :
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            return HttpResponseRedirect('/index')
        return render(request, 'user/login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        # user = User.objects.filter(username=username)
        # if not user:
        #     return HttpResponse('用户不存在！')
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print('--login user error %s' % (e))
            return HttpResponse('用户不存在!')
        password = request.POST['password']

        # 比对密码
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()
        if password_m != user.password:
            return HttpResponse('账户或密码错误！')

        # 记录会话状态
        request.session['username'] = username
        request.session['uid'] = user.id

        # 判断用户是否点选了‘记住用户名’
        # resp = HttpResponse('登录成功!')
        resp = HttpResponseRedirect('/index')
        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600*24*3)
            resp.set_cookie('uid', user.id, 3600*24*3)
        return resp

def logoff_view(request):

    # if request.session['username'] or request.session['uid']:
    #     del request.session['username'] 
    #     del request.session['uid'] 
    # resp = HttpResponseRedirect('/index')
    # if request.COOKIES.get('username') or request.COOKIES.get('uid'):
    #     resp.delete_cookie('username')
    #     resp.delete_cookie('uid')
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']
    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.COOKIES:
        resp.delete_cookie('uid')
    return resp