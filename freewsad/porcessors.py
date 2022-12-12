

def context(request):
    if request.user.is_authenticated:
        return {}
    else:
        return {}