from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Note, User

# Create your views here.

def check_login(fn):
    def wrap(request, *args, **kwargs):
        if 'username' not in request.session or 'uid' not in request.session:
                c_username = request.COOKIES.get('username')
                c_uid = request.COOKIES.get('uid')
                if not c_username or not c_uid:
                    return HttpResponseRedirect('/user/login')
                else:
                    request.session['username'] = c_username
                    request.session['uid'] = c_uid
        return fn(request, *args, **kwargs)
    return wrap

# 列出所有笔记
def list_view(request):

    notes = Note.objects.all()
    return render(request, 'note/list_note.html', locals())

# 添加新笔记
@check_login
def add_view(request):

    if request.method == 'GET':
        return render(request, 'note/add_note.html')
    elif request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        try:
            # session中取用户名来建立用户，下面创建笔记要用
            user = User.objects.get(username = request.session.get('username'))
        except Exception as e:
            print('--error-- %s' % (e))
            # 如果没有session，就在cookie中查找用户名，然后返回用户对象。用于笔记的创建
            user = User.objects.get(username = request.COOKIES.get('username'))
        if title and content:
            note = Note.objects.create(title=title, content=content, user=user)
            return HttpResponse("添加成功")
        return HttpResponseRedirect('/note/all')

# 修改文章
@check_login
def mod_view(request, pg):

    dict = {'page':pg}
    if request.method == 'GET':
        return render(request, 'note/mod_note.html', dict)
    elif request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        note = Note.objects.get(id=pg)
        note.title = title
        note.content = content
        note.save()
        
        return HttpResponseRedirect('/note/all')