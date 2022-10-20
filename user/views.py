from django.contrib import auth
from django.shortcuts import redirect, render
from .models import User, ImageModel
from django.contrib.auth import authenticate, login as loginsession
from .forms import FileUploadForm
from django.contrib import auth
from django.contrib.auth import logout
import torch
from django.conf import settings



def signup(request):
    if request.method=='GET':
        return render(request, 'signup.html')
    elif request.method=='POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        passwordcheck = request.POST.get('passwordcheck')
        is_email = re.compile(r"^[a-zA-Z]+[!#$%&'*+-/=?^_`(){|}~]*[a-zA-Z0-9]*@[\w]+\.[a-zA-Z0-9-]+[.]*[a-zA-Z0-9]+$")
        if password != passwordcheck:
            return render(request, 'signup.html', {'error': '비밀번호가 맞지 않습니다!'})
        elif username.replace(' ','') == '':
            return render(request, 'signup.html', {'error': 'username은 공백일 수 없습니다!'})
        elif is_email.match(email) == False:
            return render(request, 'signup.html', {'error': 'email을 확인해 주세요!'})
        elif password == passwordcheck:
            User.objects.create_user(username=username, password=password, email=email)
            return redirect('/login/')
    else:
        return render(request, 'signup.html', {'error': '아이디와 비밀번호를 확인해 주세요!'})

def login(request):
    if request.method=='GET':
        return render(request, 'login.html')
    elif request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        print(username, password)
        if user is not None:
            loginsession(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': '아이디와 비밀번호를 확인해 주세요!'})

def fileupload(request):
    if request.method == "GET":
        return render(request, 'fileupload.html')

def main(request):
    if request.method =='GET':
        return render(request, 'main.html')
    elif request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid(): # 사진 업로드 유효성검사
            form.save()
            form.instance.image
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True) # yolo 모델
            results = model([settings.BASE_DIR / form.instance.image.url[1:]])
            results.save(model, 'media', True) # media yolo파일로 덮음
        context = {
            'form': form
        }
        return render(request, 'fileupload.html', context)


def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/main')
    else:
        return redirect('/login')


def logout(request):
    auth.logout(request)
    return redirect('/')
