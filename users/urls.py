from django.urls import path
from .views import *
from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib.auth.views import LoginView, LogoutView
from django.views.i18n import set_language


urlpatterns = [
    path('user/<slug:slug>', ProfileView.as_view(), name='profile'),
    path('set-language/', set_language, name='set_language'),
    path('profile/update/<int:id>/', login_required(ProfileUpdate), name='profile_update'),
    path('update/info/', login_required(user_update_info), name='user_update_info'),
    path('accounts/register', register, name='register',),
    path('accounts/login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings',  settings, name='settings'),
    path('accounts/change/password/', login_required(change_password), name='change_password'),
    path('reset_passaword/', auth_view.PasswordResetView.as_view(template_name='password_reset/reset_password.html',
     title=_('Forgot Password'),
     success_url = reverse_lazy('password_reset_done_new')), name='reset_password'),
    path('reset_passaword_sent/', posword_reset_done, name='password_reset_done_new'),
    path('accounts/reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='password_reset/password_reset_confirm.html', success_url = reverse_lazy('passaword_reset_complet_new')), name='password_reset_confirm'),
    path('reset_passaword_complet/', auth_view.PasswordResetCompleteView.as_view(template_name='password_reset/reset_done.html'), name='passaword_reset_complet_new'),

 
]