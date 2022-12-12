from django.urls import path
from .views import *
from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext as _


urlpatterns = [
    path('<slug:slug>', ProfileView.as_view(), name='profile'),
    path('profile_update/<int:pk>/', login_required(ProfileViewUpdate.as_view()), name='profile_update'),
    path('user_update_info/', login_required(user_update_info), name='user_update_info'),
    path('public/<int:pk>/', login_required(Public.as_view()), name='public'),
    path('accounts/register', register, name='register',),
    path('accounts/login/', login_view, name='login'),
    path('accounts/change_password/', login_required(PasswordChange.as_view()), name='change_password'),
    path('reset_passaword/', auth_view.PasswordResetView.as_view(template_name='password_reset/reset_password.html',
     title=_('Forgot Password'),
     success_url = reverse_lazy('password_reset_done_new')), name='reset_password'),
    path('reset_passaword_sent/', posword_reset_done, name='password_reset_done_new'),
    path('accounts/reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='password_reset/password_reset_confirm.html', success_url = reverse_lazy('passaword_reset_complet_new')), name='password_reset_confirm'),
    path('reset_passaword_complet/', auth_view.PasswordResetCompleteView.as_view(template_name='password_reset/reset_done.html'), name='passaword_reset_complet_new'),
    path('follow/<int:id>', follow, name='follow'),
    path('block_user/<int:id>', block, name='block_user'),
    path('social-media/',social_media, name='social_media')
 
]