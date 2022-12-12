
from django.utils.timezone import now
from .models import Profile
from django.utils import timezone

class SetLastVisitMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated:
            Profile.objects.filter(user=request.user) \
                           .update(last_visit=timezone.now())
