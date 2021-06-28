from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.contrib.auth import logout, login

from frontlinerapp.decorators import regularuser_required, adminuser_required
from frontlinerapp.forms import SignUpForm
from django.contrib import messages

from frontlinerapp.models import CustomUser


def home(request):
    return render(request, 'index.html', locals())


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user.is_regularuser = True
            user.save()
            print(user)
            return redirect('validate_code', username=user.username)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', locals())


@login_required
@regularuser_required
def user_dashboard(request, username):
    return render(request, 'user_dashboard.html', locals())


@login_required
@adminuser_required
def admin_dashboard(request, username):
    return render(request, 'admin_dashboard.html', locals())


def signin(request):
    if request.method == 'POST':
        if 'username' in request.POST and request.POST['username'] and 'password1' in request.POST and request.POST[
            'password1']:
            username = request.POST.get('username')
            raw_password = request.POST.get('password1')
            try:
                user = CustomUser.objects.get(username=username)
                print(user)
                return redirect('paywall', username=user.username)
            except:
                messages.error(request, 'User does not exist! Check username again')
                return HttpResponseRedirect(request.path_info)
    print("post successful!")
    return render(request, 'registration/login.html', locals())


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': CustomUser.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


def validate_code(request, username):
    if request.method == 'POST':
        return redirect('signin')
    return render(request, 'registration/2FA.html', locals())


def paywall(request, username):
    if request.method == 'POST':
        user = CustomUser.objects.get(username=username)
        if user.is_regularuser:
            print('not admin')
            login(request, user)
            return redirect('user_dashboard', username=user.username)
        else:
            print('admin')
            login(request, user)
            return redirect('admin_dashboard', username=user.username)
    return render(request, 'registration/paywall.html', locals())


