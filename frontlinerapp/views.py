from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import logout, login
from pinax.referrals.models import Referral, ReferralResponse
from frontlinerapp.decorators import regularuser_required, adminuser_required
from frontlinerapp.forms import SignUpForm
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from frontlinerapp.models import CustomUser, Profile, Chat, Message
from frontlinerapp.tasks import implement_signup_money_flow, get_upper_level_referrer


def home(request):
    return render(request, 'index.html', locals())


def terms(request):
    return render(request, 'registration/terms.html', locals())


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
            return redirect('validate_code', username=user.username)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', locals())


@login_required
@regularuser_required
def user_dashboard(request, username):
    profile = Profile.objects.get(user=request.user)
    referral_responses = ReferralResponse.objects.filter(referral=profile.referral)
    level_one = get_upper_level_referrer(request.user)
    level_two = get_upper_level_referrer(level_one)
    if level_one is not None:
        profile.one_level_up_user = level_one
        profile.save()
    if level_two is not None:
        profile.two_levels_up_user = level_two
        profile.save()
    print("One level up, %s." % level_one)
    print("Two levels up, %s." % level_two)

    return render(request, 'users/index.html', locals())


@login_required
@adminuser_required
def admin_dashboard(request, username):
    users = CustomUser.objects.all()
    online_users = []
    for user in users:
        if user.online:
            online_users.append(user)
    print(online_users)
    return render(request, 'admin_dashboard.html', locals())


def signin(request):
    if request.method == 'POST':
        if 'username' in request.POST and request.POST['username'] and 'password1' in request.POST and request.POST[
            'password1']:
            username = request.POST.get('username')
            raw_password = request.POST.get('password1')
            user_exists = CustomUser.objects.filter(username__iexact=username).exists()
            user = CustomUser.objects.get(username=username)
            print(user.first_time_login)
            try:
                user = CustomUser.objects.get(username=username)
                if user.is_regularuser:
                    if user.first_time_login:
                        user.first_time_login = False
                        user.save()
                        return redirect('paywall', username=user.username)
                    else:
                        login(request, user)
                        return redirect('user_dashboard', username=user.username)
                else:
                    login(request, user)
                    return redirect('admin_dashboard', username=user.username)
            except:
                print('fuck this')
                messages.error(request, 'User does not exist! Check username again')
                return HttpResponseRedirect(request.path_info)
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


def validate_login(request):
    username = request.GET.get('username', None)
    is_correct = CustomUser.objects.filter(username__iexact=username).exists()
    password_wrong = 'password_wrong'

    data = {
        'is_correct': is_correct,
        'password_wrong': password_wrong

    }
    return JsonResponse(data)


@regularuser_required
def user_messages(request, username):
    return render(request, 'users/messages.html', locals())


@regularuser_required
def user_notifications(request, username):
    return render(request, 'users/notifications.html', locals())


@adminuser_required
def admin_messages(request, username):
    messages = Message.objects.all()
    chats = Chat.objects.all().order_by('updated_at')
    return render(request, 'admin/messages.html', locals())


@adminuser_required
def admin_notifications(request, username):
    return render(request, 'admin/notifications.html', locals())


@adminuser_required
def search_users(request, username):
    if 'search_users' in request.GET and request.GET.get('search_users'):
        user_list = CustomUser.objects.filter(username__icontains = request.GET.get('search_users'))
        print(user_list)
    return render(request, 'admin/search_users.html', locals())


@adminuser_required
def admin_settings(request, username):
    return render(request, 'admin/admin_settings.html', locals())


@adminuser_required
def user_management(request, username):
    users = CustomUser.objects.all()
    return render(request, 'admin/user_management.html', locals())


def delete_users(request):
    id = request.GET.get('id', None)
    is_deleted = False
    try:
        user = CustomUser.objects.get(id=id)
        user.delete()
        is_deleted = True
    except ObjectDoesNotExist:
        pass
    data = {
        'is_deleted': is_deleted
        }
    return JsonResponse(data)


def user_details(request, username):
    return render(request, 'admin/user_details.html', locals())


def chat_admin(request):
    if request.method == 'POST':
        author = CustomUser.objects.get(username=request.POST.get('username'))
        message = request.POST.get('message')
        other = CustomUser.objects.filter(is_regularuser=False)[0]
        try:
            chat = Chat.objects.filter(members=author).order_by('id')[0]
        except:
            chat = Chat.objects.create()
            chat.members.add(author)
            other = CustomUser.objects.get(username='testadmin')
            chat.members.add(other)
            chat.save()
        print(chat)
        message = Message.objects.create(author=author, message=message, chat=chat)
        message.save()
        data = {'sent': 'Message sent to admin!', 'message_id': message.id}
        return JsonResponse(data)


def reply_admin(request):
    if request.method == 'POST':
        author = CustomUser.objects.get(username=request.POST.get('admin'))
        message = request.POST.get('message')
        other = CustomUser.objects.get(username=request.POST.get('username'))
        chat = Chat.objects.filter(members=other).order_by('id')[0]
        message = Message.objects.create(author=author, message=message, chat=chat)
        message.save()
        chat.save()
        data = {'sent': 'Message sent to '+ other.username, 'message_id': message.id}

        return JsonResponse(data)


def admin_messages_details(request, username, id):
    chat = Chat.objects.get(id=id)
    messages = Message.objects.filter(chat=chat).order_by('id')
    admin = CustomUser.objects.get(username=username)
    return render(request, 'admin/message_details.html', locals())


def get_latest_message(request):
    id = request.GET.get('id', None)
    chat = Chat.objects.get(id=id)
    message = Message.objects.filter(chat=chat).order_by('-id')[0]
    data = {
        'id': message.id,
        'message':message.message,
        'date': naturaltime(message.pub_date)
    }
    return JsonResponse(data)