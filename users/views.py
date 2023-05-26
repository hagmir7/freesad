from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile, Public
from django.views.generic import ListView, DetailView, UpdateView, UpdateView
from django.contrib.auth.models import User
from .forms import *
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from posts.forms import PostUser
from posts.models import Post, Notification, Repo
from django.http import JsonResponse
import smtplib
from email.message import EmailMessage
from django.utils.translation import gettext_lazy as _
from .country import block_names
from ipregistry import IpregistryClient
from posts.rondom import total_rondom


# LOGIN
def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    alert = False
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if authenticate(username=username, password=password):
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('/')
            else:
                messages.add_message(request, messages.ERROR, _('Password is incorrect!'))
                return redirect('login')
        if next:
            return redirect(next)

    
    context = {'form': form,'alert':alert, 'title': _("Log in")}
    return render(request, "registration/login.html", context)

# Welcom Message   
def email_message(obj, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = obj
    msg['to'] = to
    username = 'hagmir7@gmail.com'
    msg['from'] = username
    password = 'jfpgqzkxetgyjbvo'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()



import json
import urllib.request

# REGISTER 
def register(request):
    block_name = False
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = UserCreationForm()
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                new_user = form.save(commit=False)
                username = form.cleaned_data['username']
                email = new_user.email
                new_user.save()
                if new_user is not None:
                    if new_user.is_active:
                        login(request, new_user)
                        return redirect('home')
                    
                return redirect('login')
    context = {'title': _('Register'), 'form': form, }
    return render(request, 'registrations/register.html', context)


class ProfileView(DetailView):
    model = Profile
    template_name = 'profile/profile.html'
    count_hit = True

    def get_context_data(self, *arge, **kwargs):
        context = super(ProfileView, self).get_context_data(*arge, **kwargs)
        page = get_object_or_404(Profile, slug=self.kwargs['slug'])
        title = f'{page.user.first_name} {page.user.last_name}'
        posts = Post.objects.filter(user=page.user).order_by('-date')
        repo = Repo.objects.filter(user=page.user).order_by('-date')[0:4]
        description = _('You can join now to connect with your  friends and enjoy your books and courses register now')
        context["page"] = page
        context["title"] = title
        context["posts"] = posts
        context["repo"] = repo
        context['description'] = f'{title} {description}'
        context["tags"] = title
        return context

    def post(self, request, *args, **kwargs):
        form = PostUser()
        if request.method == 'POST':
            form = PostUser(request.POST, files=request.FILES)
            if form.is_valid:
                obj = form.save(commit=False)
                obj.user = request.user
                if obj.text or obj.imageU:
                    obj.save()
                    obj.slug = f'{total_rondom}-{obj.id}'
                    obj.save()
                    messages.success(request, _("Posted Successfully"))
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
                else:
                    messages.warning(request, _('Nothig to Post'))
        context = {'form': form}
        return render(request, self.template_name, context)


class ProfileViewUpdate(UpdateView):
    model = Profile
    template_name = 'profile/update_profile.html'
    form_class = UpdateProfile
    success_url = reverse_lazy('home')
    success_message = _('Profile updated successfully!')

    def get_context_data(self, *arge, **kwargs):
        context = super(ProfileViewUpdate, self).get_context_data(
            *arge, **kwargs)
        page = get_object_or_404(Profile, id=self.kwargs['pk'])
        title = _('Update Profile')
        context["page"] = page
        context["title"] = title
        return context


 
# Follow User
def follow(request, id):
    profile = get_object_or_404(Profile, id=request.POST.get('user_id')) 
    profile_noti = Profile.objects.get(id=id)
    sender = request.user
    user = profile.user
    data = {'follow': _('Follow'), 'unfollow':_('Unfollow')}
    if profile.follow.filter(id=request.user.id).exists():
        profile.follow.remove(request.user)
        if profile.user != request.user:
            remove = Notification.objects.filter(user=user, sender=sender, profile=profile, text=_('Follow you'), not_type='follow')
            remove.delete()
        return JsonResponse(data)
    else:
        if request.user.is_authenticated:
            profile.follow.add(request.user)
            if profile.user != request.user:
                Notification.objects.create(user=user, sender=sender, profile=profile, text=_('Follow you'), not_type='follow')
            return JsonResponse(data)
                
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


# Block User
def block(request, id):
    profile = get_object_or_404(Profile, id=request.POST.get('user_block')) 
    if profile.block.filter(id=request.user.id).exists():
        profile.block.remove(request.user)
        
    else:
        if request.user.is_authenticated:
            profile.block.add(request.user)
            remove_follow = profile.follow.all()
            for user in remove_follow:
                if user == request.user:
                    profile.follow.remove(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    

def user_update_info(request):
    confirm = False
    if request.method == 'POST':
        form = UserUpdateInfo(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            confirm = True
    else:
        form = UserUpdateInfo(instance=request.user)
    context = {'form': form, 'confirm':confirm, 'title': _("Contact information")}
    return render(request, 'profile/user_update_info.html', context)



class Public(UpdateView):
    model = Public
    template_name = 'profile/public.html'
    form_class = PublicForm
    success_url = reverse_lazy('home')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Audience")
        return context


class PasswordChange(PasswordChangeView):
    template_name = 'profile/change-password.html'
    success_url = reverse_lazy('home')

class PasswordChangeDone(ListView):
    
    template_name = 'profile/change-password-done.html'
    form_class = PublicForm
    success_url = reverse_lazy('home')


def posword_reset_done(request):
    context = {'title':_("Password reset has been sent")}
    return render(request, 'password_reset/reset_password_done.html', context)


        


def social_media(request):
    message = ""
    if request.is_ajax():
        form = SocialMedia(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            message = _('Updated Successfuly')
        else:
            message = _("Data is Not valid")
    else:
        message = _("Request is Not POST")


    return JsonResponse({'message': message })
